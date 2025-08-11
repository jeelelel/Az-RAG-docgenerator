import os
import argparse
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SearchFieldDataType, SimpleField, SearchableField
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv


def create_simple_index(index_name, index_client):
    """Create a simple search index for document content"""
    print(f"Ensuring search index {index_name} exists")
    
    try:
        # Check if index exists
        existing_indexes = [idx.name for idx in index_client.list_indexes()]
        
        if index_name not in existing_indexes:
            print(f"Creating search index: {index_name}")
            
            # Define fields
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SimpleField(name="filepath", type=SearchFieldDataType.String),
                SimpleField(name="chunk_id", type=SearchFieldDataType.String),
            ]
            
            # Create the search index
            index = SearchIndex(name=index_name, fields=fields)
            index_client.create_index(index)
            print(f"Search index '{index_name}' created successfully")
        else:
            print(f"Search index '{index_name}' already exists")
    
    except Exception as e:
        print(f"Error creating index: {e}")
        raise


def chunk_text(text, chunk_size=1000, overlap=100):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        
        if end >= len(text):
            break
    
    return chunks


def process_document(file_path):
    """Process a document and extract content"""
    print(f"Processing document: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = Path(file_path).stem
        chunks = chunk_text(content)
        
        documents = []
        for i, chunk in enumerate(chunks):
            doc = {
                "id": str(uuid.uuid4()),
                "content": chunk,
                "title": title,
                "filepath": str(file_path),
                "chunk_id": f"{title}_{i}"
            }
            documents.append(doc)
        
        return documents
    
    except Exception as e:
        print(f"Error processing document {file_path}: {e}")
        return []


def main():
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--searchservice", help="Search service name")
    parser.add_argument("--index", help="Search index name")
    parser.add_argument("--documents", default="./data/sample_documents", help="Documents directory")
    
    args = parser.parse_args()
    
    # Get configuration from environment or args
    search_service = args.searchservice or os.getenv("AZURE_SEARCH_SERVICE")
    index_name = args.index or os.getenv("AZURE_SEARCH_INDEX")
    search_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
    
    if not all([search_service, index_name, search_key]):
        raise ValueError("Missing required configuration. Check your .env file or command line arguments.")
    
    # Initialize search clients
    search_endpoint = f"https://{search_service}.search.windows.net"
    credential = AzureKeyCredential(search_key)
    
    index_client = SearchIndexClient(search_endpoint, credential)
    search_client = SearchClient(search_endpoint, index_name, credential)
    
    # Create index
    create_simple_index(index_name, index_client)
    
    # Process documents
    documents_dir = Path(args.documents)
    all_documents = []
    
    for file_path in documents_dir.glob("*.md"):
        documents = process_document(file_path)
        all_documents.extend(documents)
    
    # Upload documents to search index
    if all_documents:
        print(f"Uploading {len(all_documents)} document chunks to search index...")
        try:
            result = search_client.upload_documents(documents=all_documents)
            print("Documents uploaded successfully!")
            
            # Print upload results
            success_count = 0
            for res in result:
                if res.succeeded:
                    success_count += 1
                    print(f"✓ Uploaded document chunk: {res.key}")
                else:
                    print(f"✗ Failed to upload document chunk: {res.key} - {res.error_message}")
            
            print(f"\nSummary: {success_count}/{len(all_documents)} documents uploaded successfully")
        
        except Exception as e:
            print(f"Error uploading documents: {e}")
            raise
    else:
        print("No documents found to process")


if __name__ == "__main__":
    main()

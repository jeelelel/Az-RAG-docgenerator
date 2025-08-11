import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv
import datetime


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
    """Process a document and create documents matching the existing schema"""
    print(f"Processing document: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = Path(file_path).stem
        chunks = chunk_text(content)
        
        documents = []
        for i, chunk in enumerate(chunks):
            # Create valid key without forward slashes  
            storage_path = f"sample_documents-{title}_{i}-md"
            
            doc = {
                "metadata_storage_path": storage_path,
                "content": chunk,
                "filename": f"{title}_{i}.md",
                "metadata_storage_name": f"{title}_{i}.md",
                "metadata_title": title,
                "subject": title,
                "filelocation": str(file_path),
                "metadata_storage_content_type": "text/markdown",
                "metadata_storage_size": len(chunk),
                "metadata_storage_last_modified": datetime.datetime.now().isoformat() + "Z",
                "metadata_storage_file_extension": ".md",
                "metadata_content_type": "text/markdown",
                "metadata_language": "en",
                "messageid": str(uuid.uuid4()),
                "projectid": "sample-project",
                "messagetype": "sample-document",
                "cycleids": "cycle-1",
                "groupids": "group-1"
            }
            documents.append(doc)
        
        return documents
    
    except Exception as e:
        print(f"Error processing document {file_path}: {e}")
        return []


def main():
    load_dotenv()
    
    search_service = os.getenv("AZURE_SEARCH_SERVICE")
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    search_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
    
    if not all([search_service, index_name, search_key]):
        raise ValueError("Missing required configuration. Check your .env file.")
    
    search_endpoint = f"https://{search_service}.search.windows.net"
    credential = AzureKeyCredential(search_key)
    search_client = SearchClient(search_endpoint, index_name, credential)
    
    # Process documents
    documents_dir = Path("./data/sample_documents")
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
            
            success_count = 0
            for res in result:
                if res.succeeded:
                    success_count += 1
                    print(f"✓ Uploaded document chunk: {res.key}")
                else:
                    print(f"✗ Failed to upload document chunk: {res.key} - {res.error_message}")
            
            print(f"\nSummary: {success_count}/{len(all_documents)} documents uploaded successfully")
            
            # Test search
            print("\nTesting search...")
            search_results = search_client.search(search_text="Azure OpenAI", top=3)
            for result in search_results:
                print(f"Found: {result.get('metadata_title', 'Unknown')} - Score: {result['@search.score']}")
                print(f"Content preview: {result.get('content', '')[:100]}...")
                print()
        
        except Exception as e:
            print(f"Error uploading documents: {e}")
            raise
    else:
        print("No documents found to process")


if __name__ == "__main__":
    main()

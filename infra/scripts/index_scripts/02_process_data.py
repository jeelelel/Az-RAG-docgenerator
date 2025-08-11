from openai import AzureOpenAI
import re
import time
import pypdf
from pathlib import Path
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import (AzureCliCredential, get_bearer_token_provider)
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - loaded from environment variables
search_service_name = os.getenv("AZURE_SEARCH_SERVICE_NAME", "recipe-search")
search_admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_key = os.getenv("AZURE_OPENAI_API_KEY")

# Validate required environment variables
required_vars = {
    "AZURE_SEARCH_ADMIN_KEY": search_admin_key,
    "AZURE_OPENAI_ENDPOINT": azure_openai_endpoint,
    "AZURE_OPENAI_API_KEY": azure_openai_key
}

for var_name, var_value in required_vars.items():
    if not var_value:
        raise ValueError(f"Required environment variable {var_name} is not set. Please check your .env file.")

# Local data settings
data_directory = "/workspaces/document-generation-solution-accelerator/infra/data"
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "food-recipe-index")

# Azure Search settings
search_endpoint = f"https://{search_service_name}.search.windows.net"
credential = AzureKeyCredential(search_admin_key)
search_client = SearchClient(search_endpoint, index_name, credential)
print("✅ Azure Search setup complete.")

# Function: Get Embeddings
def get_embeddings(text: str):
    """Generate embeddings using Azure OpenAI"""
    model_id = "text-embedding-3-large"  # CORRECTED: Use the actual deployed model
    openai_api_version = "2024-02-15-preview"
    
    try:
        # Try Azure CLI credential first
        ad_token_provider = get_bearer_token_provider(
            AzureCliCredential(), "https://cognitiveservices.azure.com/.default"
        )
        client = AzureOpenAI(
            api_version=openai_api_version,
            azure_endpoint=azure_openai_endpoint,
            azure_ad_token_provider=ad_token_provider
        )
        embedding = client.embeddings.create(input=text, model=model_id).data[0].embedding
        return embedding
    except Exception as e:
        print(f"⚠️  Azure CLI auth failed, using API key: {e}")
        # Fallback to API key
        client = AzureOpenAI(
            api_key=azure_openai_key,
            api_version=openai_api_version,
            azure_endpoint=azure_openai_endpoint
        )
        embedding = client.embeddings.create(input=text, model=model_id).data[0].embedding
        return embedding

# Function: Clean Spaces with Regex
def clean_spaces_with_regex(text):
    # Use a regular expression to replace multiple spaces with a single space
    cleaned_text = re.sub(r'\s+', ' ', text)
    # Use a regular expression to replace consecutive dots with a single dot
    cleaned_text = re.sub(r'\.{2,}', '.', cleaned_text)
    return cleaned_text.strip()

# Function: Chunk Data
def chunk_data(text):
    tokens_per_chunk = 500  # Increased for recipe content
    text = clean_spaces_with_regex(text)

    sentences = text.split('. ')  # Split text into sentences
    chunks = []
    current_chunk = ''
    current_chunk_token_count = 0

    # Iterate through each sentence
    for sentence in sentences:
        # Split sentence into tokens
        tokens = sentence.split()

        # Check if adding the current sentence exceeds tokens_per_chunk
        if current_chunk_token_count + len(tokens) <= tokens_per_chunk:
            # Add the sentence to the current chunk
            if current_chunk:
                current_chunk += '. ' + sentence
            else:
                current_chunk += sentence
            current_chunk_token_count += len(tokens)
        else:
            # Add current chunk to chunks list and start a new chunk
            if current_chunk:  # Only add non-empty chunks
                chunks.append(current_chunk)
            current_chunk = sentence
            current_chunk_token_count = len(tokens)

    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

# Function: Prepare Search Document
def prepare_search_doc(content, filename):
    """Prepare search documents matching your index schema"""
    chunks = chunk_data(content)
    results = []
    
    # Create document ID from filename
    document_id = filename.replace('.pdf', '').replace(' ', '_').replace('-', '_')
    
    for idx, chunk in enumerate(chunks, 1):
        chunk_id = f"{document_id}_{str(idx).zfill(3)}"
        
        print(f"  📝 Processing chunk {idx}/{len(chunks)}: {len(chunk)} chars")

        try:
            v_contentVector = get_embeddings(str(chunk))
            print(f"  ✅ Generated embedding for chunk {idx}")
        except Exception as e:
            print(f"  ❌ Error getting embedding for chunk {idx}: {e}")
            print(f"  🔄 Retrying after 10 seconds...")  # Reduced retry time
            time.sleep(10)
            try:
                v_contentVector = get_embeddings(str(chunk))
                print(f"  ✅ Retry successful for chunk {idx}")
            except Exception as e:
                print(f"  ❌ Retry failed for chunk {idx}: {e}")
                v_contentVector = []

        # Match your index schema from 01_create_search_index.py
        result = {
            "id": chunk_id,
            "chunk_id": chunk_id,
            "content": chunk,
            "title": filename.replace('.pdf', '').replace('-', ' ').title(),
            "filepath": str(Path(data_directory) / filename),
            "url": f"file://{Path(data_directory) / filename}",
            "contentVector": v_contentVector
        }
        results.append(result)
    
    return results

def main():
    """Main function to process local PDF files"""
    print("🚀 Starting local PDF processing...")
    print(f"📁 Data directory: {data_directory}")
    print(f"🔍 Target index: {index_name}")
    print(f"🤖 Using embedding model: text-embedding-3-large")  # Added model info
    
    # Get all PDF files from local directory
    pdf_files = list(Path(data_directory).glob("*.pdf"))
    print(f"📚 Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    docs = []
    counter = 0
    total_chunks = 0

    for pdf_path in pdf_files:
        print(f"\n📄 Processing: {pdf_path.name}")
        
        try:
            # Read PDF file
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Check if PDF is password protected
                if pdf_reader.is_encrypted:
                    print(f"  ⚠️  Skipping password-protected file: {pdf_path.name}")
                    continue
                
                filename = pdf_path.name
                
                # Extract text from all pages
                text = ''
                num_pages = len(pdf_reader.pages)
                print(f"  📖 Extracting text from {num_pages} pages")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
                
                if not text.strip():
                    print(f"  ⚠️  No text extracted from {filename}")
                    continue
                
                print(f"  ✅ Extracted {len(text)} characters")
                
                # Prepare search documents
                result = prepare_search_doc(text, filename)
                docs.extend(result)
                total_chunks += len(result)
                
                print(f"  ✅ Created {len(result)} chunks from {filename}")
                
                counter += 1
                
                # Upload in batches of 20 documents (reduced for better reliability)
                if len(docs) >= 20:
                    print(f"\n📤 Uploading batch of {len(docs)} documents...")
                    try:
                        upload_result = search_client.upload_documents(documents=docs)
                        successful = sum(1 for r in upload_result if r.succeeded)
                        failed = len(docs) - successful
                        print(f"  ✅ Successfully uploaded {successful}/{len(docs)} documents")
                        if failed > 0:
                            print(f"  ⚠️  {failed} documents failed to upload")
                        docs = []
                    except Exception as e:
                        print(f"  ❌ Error uploading batch: {e}")
                        docs = []
        
        except Exception as e:
            print(f"  ❌ Error processing {pdf_path.name}: {e}")
            continue

    # Upload remaining documents
    if docs:
        print(f"\n📤 Uploading final batch of {len(docs)} documents...")
        try:
            upload_result = search_client.upload_documents(documents=docs)
            successful = sum(1 for r in upload_result if r.succeeded)
            failed = len(docs) - successful
            print(f"  ✅ Successfully uploaded {successful}/{len(docs)} documents")
            if failed > 0:
                print(f"  ⚠️  {failed} documents failed to upload")
        except Exception as e:
            print(f"  ❌ Error uploading final batch: {e}")

    print(f"\n🎉 Processing complete!")
    print(f"   📚 Files processed: {counter}")
    print(f"   📝 Total chunks created: {total_chunks}")
    print(f"   🔍 Index: {index_name}")
    print(f"   🔗 View at: https://portal.azure.com/")

if __name__ == "__main__":
    main()
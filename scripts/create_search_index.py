#!/usr/bin/env python3
"""
Simple script to create an Azure AI Search index for your PDF documents.
This version uses direct configuration instead of Key Vault for simplicity.
"""

from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureCliCredential
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SemanticConfiguration,
    SemanticSearch,
    SemanticPrioritizedFields,
    SemanticField,
    SearchIndex
)

# ===== CONFIGURATION - UPDATE THESE VALUES =====
# Your Azure AI Search service details
SEARCH_SERVICE_NAME = "friday4julysearch"  # Your search service name
SEARCH_ADMIN_KEY = "YOUR_ADMIN_KEY_HERE"   # Get this from Azure Portal > Search Service > Keys

# Your Azure OpenAI details (needed for vector search)
AZURE_OPENAI_ENDPOINT = "https://your-openai-service.openai.azure.com/"  # Your OpenAI endpoint
AZURE_OPENAI_KEY = "YOUR_OPENAI_KEY_HERE"   # Your OpenAI key
EMBEDDING_MODEL = "text-embedding-ada-002"  # Your embedding model deployment name

# Index configuration
INDEX_NAME = "my-pdf-documents"  # You can use "crossmark-21july" to replace your existing index

# Authentication method (choose one)
USE_CLI_AUTH = True  # Set to True if you're logged in with 'az login'
USE_API_KEY = False  # Set to True if you want to use the admin key above

def create_pdf_search_index():
    """Creates an Azure AI Search index optimized for PDF documents."""
    
    # Set up authentication
    search_endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
    
    if USE_CLI_AUTH:
        print("Using Azure CLI authentication...")
        credential = AzureCliCredential()
    else:
        print("Using API key authentication...")
        credential = AzureKeyCredential(SEARCH_ADMIN_KEY)
    
    # Create the search index client
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
    
    # Define the index schema for PDF documents
    fields = [
        # Required fields
        SearchField(name="id", type=SearchFieldDataType.String, key=True),
        
        # Content fields
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True, analyzer_name="en.microsoft"),
        SearchField(name="title", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="chunk_id", type=SearchFieldDataType.String),
        
        # Metadata fields
        SearchField(name="filepath", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="page_number", type=SearchFieldDataType.Int32, filterable=True),
        SearchField(name="chunk_index", type=SearchFieldDataType.Int32, filterable=True),
        
        # Vector field for semantic search
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,  # For text-embedding-ada-002
            vector_search_profile_name="myHnswProfile",
        ),
    ]
    
    # Configure vector search (for semantic similarity)
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="myHnsw")
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
                vectorizer_name="myOpenAI"
            )
        ],
        vectorizers=[
            AzureOpenAIVectorizer(
                vectorizer_name="myOpenAI",
                kind="azureOpenAI",
                parameters=AzureOpenAIVectorizerParameters(
                    resource_url=AZURE_OPENAI_ENDPOINT,
                    deployment_name=EMBEDDING_MODEL,
                    model_name=EMBEDDING_MODEL
                )
            )
        ]
    )
    
    # Configure semantic search (for enhanced relevance)
    semantic_config = SemanticConfiguration(
        name="pdf-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            keywords_fields=[SemanticField(field_name="filepath")],
            content_fields=[SemanticField(field_name="content")],
        ),
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_config])
    
    # Create the index
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )
    
    try:
        result = index_client.create_or_update_index(index)
        print(f"✅ Search index '{result.name}' created/updated successfully!")
        print(f"📁 Index fields: {len(result.fields)} fields defined")
        print(f"🔍 Vector search: Enabled with {vector_search.profiles[0].name}")
        print(f"🧠 Semantic search: Enabled with {semantic_config.name}")
        return True
    except Exception as e:
        print(f"❌ Error creating index: {str(e)}")
        return False

def main():
    """Main function to create the search index."""
    print("🚀 Creating Azure AI Search index for PDF documents...")
    print(f"📋 Search Service: {SEARCH_SERVICE_NAME}")
    print(f"📋 Index Name: {INDEX_NAME}")
    print("-" * 50)
    
    success = create_pdf_search_index()
    
    if success:
        print("\n✅ Index creation completed successfully!")
        print("\n📝 Next steps:")
        print("1. Upload your PDF files to the search index")
        print("2. Use the search index in your application")
        print(f"3. Index endpoint: https://{SEARCH_SERVICE_NAME}.search.windows.net/indexes/{INDEX_NAME}")
    else:
        print("\n❌ Index creation failed. Please check the error messages above.")

if __name__ == "__main__":
    main()

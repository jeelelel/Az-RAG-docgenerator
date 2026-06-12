#!/usr/bin/env python3
"""
Simple script to create an Azure AI Search index for PDF documents.
Reads configuration from azure_config.ini file.
"""

import configparser
import os
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

def load_config():
    """Load configuration from azure_config.ini file."""
    config_file = "azure_config.ini"
    if not os.path.exists(config_file):
        print(f"❌ Configuration file '{config_file}' not found!")
        print(f"Please create the file and add your Azure credentials.")
        return None
    
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def create_search_index():
    """Create an Azure AI Search index for PDF documents."""
    
    # Load configuration
    config = load_config()
    if not config:
        return False
    
    try:
        # Get configuration values
        search_service = config['AZURE_SEARCH']['service_name']
        admin_key = config['AZURE_SEARCH']['admin_key']
        index_name = config['AZURE_SEARCH']['index_name']
        
        openai_endpoint = config['AZURE_OPENAI']['endpoint']
        openai_key = config['AZURE_OPENAI']['api_key']
        embedding_model = config['AZURE_OPENAI']['embedding_model']
        
        use_cli_auth = config['AUTHENTICATION'].getboolean('use_cli_auth')
        
        print(f"🔧 Configuration loaded:")
        print(f"   Search Service: {search_service}")
        print(f"   Index Name: {index_name}")
        print(f"   Authentication: {'Azure CLI' if use_cli_auth else 'API Key'}")
        print("-" * 50)
        
    except KeyError as e:
        print(f"❌ Missing configuration key: {e}")
        print("Please check your azure_config.ini file.")
        return False
    
    # Set up authentication
    search_endpoint = f"https://{search_service}.search.windows.net"
    
    if use_cli_auth:
        print("🔐 Using Azure CLI authentication...")
        try:
            credential = AzureCliCredential()
        except Exception as e:
            print(f"❌ Azure CLI authentication failed: {e}")
            print("Make sure you're logged in with 'az login'")
            return False
    else:
        print("🔐 Using API key authentication...")
        if admin_key == "YOUR_ADMIN_KEY_HERE":
            print("❌ Please update the admin_key in azure_config.ini")
            return False
        credential = AzureKeyCredential(admin_key)
    
    # Create the search index client
    try:
        index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
    except Exception as e:
        print(f"❌ Failed to create search client: {e}")
        return False
    
    # Define the index schema optimized for PDF documents
    fields = [
        # Required primary key
        SearchField(name="id", type=SearchFieldDataType.String, key=True),
        
        # Content fields for search
        SearchField(
            name="content", 
            type=SearchFieldDataType.String, 
            searchable=True, 
            analyzer_name="en.microsoft"
        ),
        SearchField(
            name="title", 
            type=SearchFieldDataType.String, 
            searchable=True,
            sortable=True
        ),
        
        # Metadata fields
        SearchField(
            name="filepath", 
            type=SearchFieldDataType.String, 
            filterable=True,
            facetable=True
        ),
        SearchField(
            name="chunk_id", 
            type=SearchFieldDataType.String,
            filterable=True
        ),
        SearchField(
            name="page_number", 
            type=SearchFieldDataType.Int32, 
            filterable=True,
            sortable=True
        ),
        
        # Vector field for semantic search using embeddings
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,  # Standard for text-embedding-ada-002
            vector_search_profile_name="myHnswProfile",
        ),
    ]
    
    # Configure vector search for semantic similarity
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
                    resource_url=openai_endpoint,
                    deployment_name=embedding_model,
                    model_name=embedding_model
                )
            )
        ]
    )
    
    # Configure semantic search for enhanced relevance
    semantic_config = SemanticConfiguration(
        name="pdf-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            keywords_fields=[SemanticField(field_name="filepath")],
            content_fields=[SemanticField(field_name="content")],
        ),
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_config])
    
    # Create the search index
    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )
    
    try:
        print("🚀 Creating/updating search index...")
        result = index_client.create_or_update_index(index)
        
        print(f"✅ Search index '{result.name}' created/updated successfully!")
        print(f"📊 Index statistics:")
        print(f"   • Fields: {len(result.fields)}")
        print(f"   • Vector search: Enabled")
        print(f"   • Semantic search: Enabled")
        print(f"   • Endpoint: {search_endpoint}/indexes/{index_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating index: {str(e)}")
        print("\n🔍 Common solutions:")
        print("   • Check your search service name and credentials")
        print("   • Verify you have sufficient permissions")
        print("   • Ensure your Azure OpenAI deployment exists")
        return False

def main():
    """Main function."""
    print("🚀 Azure AI Search Index Creator for PDF Documents")
    print("=" * 55)
    
    success = create_search_index()
    
    if success:
        print("\n🎉 SUCCESS! Your search index is ready.")
        print("\n📝 Next steps:")
        print("   1. Process your PDF documents")
        print("   2. Extract text and create chunks")
        print("   3. Upload documents to the index")
        print("   4. Start searching your PDFs!")
        
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        print("\n💡 Need help? Check:")
        print("   • Your azure_config.ini file has correct values")
        print("   • You're logged in with 'az login' (if using CLI auth)")
        print("   • Your Azure resources exist and are accessible")

if __name__ == "__main__":
    main()

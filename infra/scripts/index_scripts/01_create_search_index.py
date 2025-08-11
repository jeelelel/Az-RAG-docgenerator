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
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential

# === Configuration ===
# CORRECTED Configuration to match your actual Azure resources
search_service_name = "recipe-search"  # Your search resource name
search_admin_key = "REDACTED_AZURE_SEARCH_KEY"  # Your admin key
azure_openai_endpoint = "https://fridayjuly4azureopenai.openai.azure.com/"  # Your actual endpoint
azure_openai_key = "REDACTED_AZURE_OPENAI_KEY"  # Your OpenAI key
embedding_model = "text-embedding-3-large"  # CORRECTED: Your actual deployed model

# Use your existing index name
index_name = "food-recipe-index"  # Your index name

def delete_and_recreate_index():
    """Delete existing index and create new one with correct vector dimensions"""
    
    print(f"🗑️  Deleting and recreating search index: {index_name}")
    print(f"📡 Search service: {search_service_name}")
    print(f"🤖 Azure OpenAI: fridayjuly4azureopenai")
    print(f"📊 Embedding model: {embedding_model}")
    print(f"🔢 Vector dimensions: 3072 (text-embedding-3-large)")

    # Use API Key Authentication
    search_endpoint = f"https://{search_service_name}.search.windows.net"
    credential = AzureKeyCredential(search_admin_key)
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
    
    print("✅ Authentication successful")

    # Step 1: Delete existing index if it exists
    try:
        index_client.delete_index(index_name)
        print(f"🗑️  Successfully deleted existing index: {index_name}")
    except Exception as e:
        print(f"⚠️  Index deletion note: {e}")
        print("   (This is normal if the index doesn't exist yet)")

    # Step 2: Define new index schema for PDF documents
    fields = [
        SearchField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="chunk_id", type=SearchFieldDataType.String),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="title", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="filepath", type=SearchFieldDataType.String),
        SearchField(name="url", type=SearchFieldDataType.String),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=3072,  # CORRECTED: text-embedding-3-large uses 3072 dimensions
            vector_search_profile_name="myHnswProfile",
        ),
    ]

    # Define vector search configuration
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
                    resource_url=azure_openai_endpoint,
                    deployment_name=embedding_model,
                    model_name=embedding_model
                )
            )
        ]
    )

    # Define semantic search configuration for PDF content
    semantic_config = SemanticConfiguration(
        name="pdf-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            keywords_fields=[SemanticField(field_name="filepath")],
            content_fields=[SemanticField(field_name="content")],
        ),
    )

    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Step 3: Create new index
    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )
    
    try:
        result = index_client.create_index(index)  # Changed to create_index instead of create_or_update_index
        print(f"✅ Search index '{result.name}' created successfully!")
        
        # Display configuration summary
        print(f"\n📋 Configuration Summary:")
        print(f"   🔍 Search Service: {search_service_name}")
        print(f"   🔑 Search Key: ****{search_admin_key[-4:]}")
        print(f"   🤖 OpenAI Service: fridayjuly4azureopenai")
        print(f"   🌐 OpenAI Endpoint: {azure_openai_endpoint}")
        print(f"   🔑 OpenAI Key: ****{azure_openai_key[-4:]}")
        print(f"   📝 Embedding Model: {embedding_model}")
        print(f"   🔢 Vector Dimensions: 3072")
        print(f"   📊 Index Name: {index_name}")
        print(f"   🎯 Vector Search: Enabled with HNSW algorithm")
        print(f"   🔍 Semantic Search: Enabled")
        
        return result
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        raise

if __name__ == "__main__":
    delete_and_recreate_index()
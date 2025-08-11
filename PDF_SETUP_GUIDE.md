# Step-by-Step Guide: Setting Up Azure AI Search for Your PDFs

## Prerequisites
You need to have the following Azure resources:
- ✅ Azure AI Search service: `friday4julysearch` 
- ✅ Azure OpenAI service (for embeddings)
- 📁 PDF documents you want to search

## Step 1: Install Required Python Packages

Run these commands in your terminal:

```bash
pip install azure-search-documents
pip install azure-identity
pip install azure-core
```

## Step 2: Get Your Azure Credentials

### Option A: Using Azure CLI (Recommended)
1. Login to Azure CLI:
   ```bash
   az login
   ```
2. Set your subscription:
   ```bash
   az account set --subscription "your-subscription-id"
   ```

### Option B: Using API Keys
1. Go to Azure Portal
2. Navigate to your Search Service: `friday4julysearch`
3. Go to "Keys" section
4. Copy the "Primary admin key"

## Step 3: Configure the Script

Edit the file `my_pdf_search_index.py` and update these values:

```python
# Your Azure AI Search service details
SEARCH_SERVICE_NAME = "friday4julysearch"  # ✅ Already correct
SEARCH_ADMIN_KEY = "paste-your-admin-key-here"  # If using API key auth

# Your Azure OpenAI details
AZURE_OPENAI_ENDPOINT = "https://your-openai-service.openai.azure.com/"
AZURE_OPENAI_KEY = "your-openai-key"
EMBEDDING_MODEL = "text-embedding-ada-002"  # Or your deployment name

# Index name - you can choose:
INDEX_NAME = "crossmark-21july"  # Use existing, OR
INDEX_NAME = "my-new-pdf-index"  # Create new one
```

## Step 4: Find Your Azure OpenAI Details

1. Go to Azure Portal
2. Find your Azure OpenAI resource
3. Go to "Keys and Endpoint"
4. Copy the endpoint URL and one of the keys
5. Go to "Model deployments" to see your embedding model name

## Step 5: Run the Script

```bash
python my_pdf_search_index.py
```

## Step 6: Upload Your PDF Documents

After creating the index, you'll need to:
1. Extract text from your PDFs
2. Split the text into chunks
3. Generate embeddings
4. Upload to the search index

This typically requires a separate script for document processing.

## Common Issues and Solutions

### Issue: "Import could not be resolved"
**Solution**: Install the required packages:
```bash
pip install azure-search-documents azure-identity azure-core
```

### Issue: "Authentication failed"
**Solution**: 
- If using CLI: Run `az login` and `az account show`
- If using API key: Verify the key is correct in Azure Portal

### Issue: "Resource not found"
**Solution**: 
- Verify your search service name is exactly "friday4julysearch"
- Check you're in the right subscription and resource group

### Issue: "OpenAI endpoint not found"
**Solution**:
- Make sure you have an Azure OpenAI service deployed
- Verify the endpoint URL format: `https://your-service.openai.azure.com/`
- Ensure you have an embedding model deployed (like text-embedding-ada-002)

## Next Steps After Index Creation

1. **Document Processing**: Create a script to extract text from PDFs
2. **Chunking**: Split documents into searchable chunks
3. **Indexing**: Upload the processed documents to your search index
4. **Search Application**: Build a search interface to query your documents

Would you like me to help you with any of these next steps?

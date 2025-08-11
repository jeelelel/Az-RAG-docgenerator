# 🚀 Complete Guide: Setting Up Azure AI Search for Your PDFs

## What You Have vs What You Need

✅ **What you already have:**
- Azure AI Search service: `friday4julysearch`
- Search index: `crossmark-21july`

❓ **What you need to configure:**
- Azure OpenAI service (for embeddings/vector search)
- Authentication setup
- PDF document processing

## Step 1: Login to Azure

```bash
az login
```

This will open a browser window for you to sign in to Azure.

## Step 2: Find Your Azure OpenAI Service

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "OpenAI" or "Cognitive Services"
3. Look for your Azure OpenAI resource
4. Note down:
   - **Endpoint URL** (e.g., `https://your-openai.openai.azure.com/`)
   - **API Key** (under "Keys and Endpoint")
   - **Embedding Model Name** (under "Model deployments")

## Step 3: Configure Your Settings

Edit the file `azure_config.ini`:

```ini
[AZURE_SEARCH]
service_name = friday4julysearch
admin_key = YOUR_ADMIN_KEY_HERE
index_name = crossmark-21july

[AZURE_OPENAI]
endpoint = https://your-openai-service.openai.azure.com/
api_key = YOUR_OPENAI_KEY_HERE
embedding_model = text-embedding-ada-002

[AUTHENTICATION]
use_cli_auth = True
```

**To get your Search Admin Key:**
1. Go to Azure Portal
2. Find your search service: `friday4julysearch`
3. Click "Keys" in the left menu
4. Copy the "Primary admin key"

## Step 4: Run the Index Creation Script

```bash
python create_pdf_index.py
```

This will:
- ✅ Connect to your search service
- ✅ Create/update the index schema
- ✅ Set up vector search for semantic similarity
- ✅ Configure fields optimized for PDF content

## Step 5: Process Your PDF Documents

After creating the index, you'll need a separate script to:

1. **Extract text from PDFs**
2. **Split into searchable chunks**
3. **Generate embeddings**
4. **Upload to search index**

Would you like me to create this PDF processing script next?

## Understanding Your Current Setup

Your search service `friday4julysearch` with index `crossmark-21july` likely already contains some documents. The script above will:

- **Keep existing data** (if any)
- **Update the schema** to be optimized for PDF documents
- **Add vector search capabilities** for better semantic search

## Troubleshooting

### "Please run 'az login'"
**Solution:** Run `az login` in your terminal and sign in to Azure.

### "Configuration file not found"
**Solution:** Make sure you have the `azure_config.ini` file with your actual Azure credentials.

### "OpenAI endpoint not found"
**Solution:** You need an Azure OpenAI service. If you don't have one:
1. Go to Azure Portal
2. Create a new "Azure OpenAI" resource
3. Deploy an embedding model (like text-embedding-ada-002)

### Want to use existing index without changes?
Set `index_name = crossmark-21july` in your config file and the script will update it.

### Want to create a new index?
Set `index_name = my-new-pdf-index` to create a fresh index.

## What Happens Next?

Once your index is set up, you can:
1. **Upload PDFs** using a document processing script
2. **Search your documents** using the Azure Search APIs
3. **Build a search application** to query your PDF content

Let me know which step you'd like help with next!

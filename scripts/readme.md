# Document Generator RAG

## Overview
AI-powered document search and generation using Azure AI services. This application allows users to generate professional documents by leveraging Azure OpenAI and Azure AI Search capabilities.

## Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Azure OpenAI resource
- Azure AI Search service
- Azure subscription

### Installation
1. Install Python dependencies:
   ```bash
   pip install --user -r requirements.txt
   ```

2. Install frontend dependencies:
   ```bash
   cd src/frontend
   npm install
   ```

## Configuration

### Environment Variables
Create a `.env` file in the `src` directory based on the example below:

```env
# Application Environment
APP_ENV=dev

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_MODEL=gpt-4o
AZURE_OPENAI_EMBEDDING_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_EMBEDDING_KEY=your-azure-openai-key
AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Azure AI Search Configuration
AZURE_SEARCH_SERVICE=your-search-service-name
AZURE_SEARCH_INDEX=your-index-name
AZURE_SEARCH_KEY=your-search-service-key
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net

# UI Settings
UI_TITLE=Document Generator RAG
UI_CHAT_TITLE=Document Generator RAG
UI_CHAT_DESCRIPTION=AI-powered document search and generation using Azure AI services

# Authentication (optional - disabled for local development)
AZURE_USE_AUTHENTICATION=false
AZURE_ENFORCE_ACCESS_CONTROL=false

# AI Search Settings
AZURE_SEARCH_USE_SEMANTIC_SEARCH=true
AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG=default
AZURE_SEARCH_TOP_K=3
AZURE_SEARCH_ENABLE_IN_DOMAIN=true

# AI Foundry Settings (optional)
AZURE_AI_AGENT_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_AI_AGENT_API_VERSION=2024-07-01-preview
```

### Required Azure Resources

#### 1. Azure OpenAI Resource
- Deploy a GPT-4o model for text generation
- Deploy a text-embedding-3-large model for embeddings
- Note the endpoint and API key

#### 2. Azure AI Search Service
- Create a search service in your preferred region
- Create an index for your documents (e.g., "pdl-index")
- Note the service name, endpoint, and admin key

## Running the Application

### Backend Server
1. Navigate to the backend directory:
   ```bash
   cd src/backend
   ```

2. Start the Python backend server:
   ```bash
   python main.py
   ```
   The backend will run on `http://localhost:50505`

### Frontend Server
1. Navigate to the frontend directory:
   ```bash
   cd src/frontend
   ```

2. Start the React development server:
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:5176`

## Using the Application

### Document Generation Workflow
1. **Generate Tab**: 
   - Ask AI to generate a document (e.g., "Generate a promissory note for $50,000")
   - The AI will create a structured document template

2. **Generate Draft Button**: 
   - Click the "Generate Draft" button after AI responds
   - This creates a draft document with sections

3. **Draft Tab**: 
   - Edit and customize the generated document sections
   - Review and modify content as needed

4. **Export Document**: 
   - Click "Export Document" to download as a Word document
   - Documents are exported in professional Times New Roman format

### Features
- **AI-powered document generation** using GPT-4o
- **Semantic search** across your document corpus
- **Professional Word export** with proper formatting
- **Section-based editing** for easy customization
- **Real-time document drafting** and editing

## Troubleshooting

### Common Issues
1. **Backend not starting**: Check your `.env` file has all required Azure credentials
2. **Frontend build errors**: Ensure Node.js version is 16 or higher
3. **Export button disabled**: Ensure all document sections are loaded and title is set
4. **Draft tab blank**: Check browser console for errors and verify document generation completed

### Debug Mode
The application includes extensive logging. Check browser console for debug messages prefixed with:
- 🎯 (Draft component)
- 🔍 (Processing)
- 🚀 (Actions)
- ✅/❌ (Status indicators)

## Development Notes

### Project Structure
```
src/
├── backend/          # Python FastAPI backend
├── frontend/         # React TypeScript frontend
├── .env             # Environment variables
└── requirements.txt # Python dependencies
```

### API Endpoints
- `/ask` - Document generation requests
- `/chat` - Chat functionality  
- `/conversation` - Conversation management
- `/document` - Document operations
- `/frontend_settings` - UI configuration

## Optional Features

### Cosmos DB Integration (Currently Disabled)
For conversation history storage, you can enable Cosmos DB by adding these environment variables:

```env
# Azure Cosmos DB Configuration
AZURE_COSMOSDB_DATABASE=conversationhistory
AZURE_COSMOSDB_ACCOUNT=your-cosmos-account
AZURE_COSMOSDB_ACCOUNT_KEY=your-cosmos-key
AZURE_COSMOSDB_CONVERSATIONS_CONTAINER=conversations
```

### Authentication (Currently Disabled)
For production deployments, enable authentication:

```env
AZURE_USE_AUTHENTICATION=true
AZURE_ENFORCE_ACCESS_CONTROL=true
```

### Document Data Ingestion
If you need to add documents to your search index, you can use the data preparation scripts in the `/scripts` folder. This allows the AI to search through your document corpus when generating responses.

#### Basic Data Ingestion
1. Place your documents in a local folder or Azure Blob Storage
2. Create a `config.json` file with your search service configuration:

```json
[
    {
        "data_path": "<local path to your documents>",
        "location": "westus2", 
        "subscription_id": "<your subscription id>",
        "resource_group": "<your resource group>",
        "search_service_name": "friday4julysearch",
        "index_name": "pdl-index",
        "chunk_size": 1024,
        "token_overlap": 128,
        "semantic_config_name": "default",
        "language": "en",
        "vector_config_name": "default"
    }
]
```

3. Run the data preparation script:
```bash
python data_preparation.py --config config.json --njobs=4
```

This will index your documents so the AI can reference them when generating documents.

## Support

### Getting Help
- Check the browser console for debug messages
- Verify all Azure resources are properly configured
- Ensure environment variables match your Azure resource names and keys
- Test backend connectivity at `http://localhost:50505/health` (if health endpoint exists)

### Known Limitations
- Authentication is currently disabled for local development
- Cosmos DB conversation history is optional
- Document export currently supports Word format only
- Frontend requires modern browser with ES6+ support

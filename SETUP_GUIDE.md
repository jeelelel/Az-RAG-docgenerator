# Local Development Setup

## Prerequisites

- Python 3.11+
- Node.js 18+
- Azure AI Search service
- Azure OpenAI service

## Environment Variables

Copy `.env.example` to `.env` and fill in the following:

```
AZURE_SEARCH_SERVICE=<your-search-service-name>
AZURE_SEARCH_KEY=<your-search-admin-key>
AZURE_SEARCH_INDEX=<your-index-name>
AZURE_OPENAI_ENDPOINT=<https://your-openai-service.openai.azure.com/>
AZURE_OPENAI_KEY=<your-openai-key>
AZURE_OPENAI_MODEL=<your-deployment-name>
```

## Running Locally

**Terminal 1 — Backend (port 8000):**
```bash
cd src
python app.py
```

**Terminal 2 — Frontend (port 5173):**
```bash
cd src/frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Routes

| Path | Description |
|------|-------------|
| `/` | Dashboard |
| `/#/chat` | Browse and search documents |
| `/#/generate` | AI document generation |
| `/#/draft` | Edit and export generated drafts |

## Troubleshooting

- **Backend not reachable**: Confirm it's running on port 8000 — the frontend proxy is configured for that port.
- **Search returns no results**: Verify your index name and search key in `.env`.
- **Export disabled in Draft**: The export button enables only when all sections have content and the title field is non-empty.

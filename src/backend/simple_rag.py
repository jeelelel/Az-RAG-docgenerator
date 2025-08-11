"""
Simple RAG implementation without Azure AI Foundry agents
Uses Azure OpenAI and Azure Search directly
"""
import os
import json
from typing import Dict, Any, List, AsyncGenerator
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AsyncAzureOpenAI
from backend.settings import app_settings

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


class SimpleRAG:
    def __init__(self):
        self.search_client = None
        self.openai_client = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize Azure Search and OpenAI clients"""
        try:
            # Initialize Azure Search client
            if app_settings.datasource:
                self.search_client = SearchClient(
                    endpoint=app_settings.datasource.endpoint,
                    index_name=app_settings.datasource.index,
                    credential=AzureKeyCredential(app_settings.datasource.key)
                )
                print(f"Initialized Azure Search client for endpoint: {app_settings.datasource.endpoint}")
                print(f"Using index: {app_settings.datasource.index}")
            else:
                print("No datasource configuration found")
            
            # Initialize Azure OpenAI client using environment variables directly
            openai_key = os.getenv("AZURE_OPENAI_KEY")
            openai_endpoint = app_settings.azure_openai.endpoint
            
            if openai_key and openai_endpoint:
                self.openai_client = AsyncAzureOpenAI(
                    azure_endpoint=openai_endpoint,
                    api_key=openai_key,
                    api_version="2024-02-01"
                )
                print(f"Initialized OpenAI client for endpoint: {openai_endpoint}")
            else:
                print(f"Missing OpenAI credentials: key={'[SET]' if openai_key else '[MISSING]'}, endpoint={openai_endpoint}")
        except Exception as e:
            print(f"Error initializing SimpleRAG clients: {e}")
    
    async def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents with improved robustness"""
        try:
            if not self.search_client:
                print("Search client not initialized")
                return []
                
            print(f"Searching for: '{query}' in index: {app_settings.datasource.index if app_settings.datasource else 'None'}")
            
            # Try different search strategies
            search_strategies = [
                {"search_text": query, "search_mode": "any"},
                {"search_text": query, "search_mode": "all"},
                {"search_text": f'"{query}"'},  # Exact phrase
                {"search_text": "*", "search_mode": "any"}  # Fallback to all documents
            ]
            
            for i, strategy in enumerate(search_strategies):
                try:
                    print(f"Strategy {i+1}: {strategy}")
                    
                    # Prepare search parameters - start with basic fields
                    search_params = {
                        "top": top_k,
                        "include_total_count": True,
                        "highlight_fields": "content"
                        # Removed select parameter - let it return all available fields
                    }
                    search_params.update(strategy)
                    
                    results = await self.search_client.search(**search_params)
                    
                    documents = []
                    total_count = 0
                    
                    async for doc in results:
                        total_count += 1
                        content = doc.get('content', '').strip()
                        
                        # Skip documents with no meaningful content
                        if len(content) < 10:
                            continue
                        
                        # Try different field names for source/filename
                        source = (doc.get('sourceurl') or 
                                doc.get('filename') or 
                                doc.get('filelocation') or 
                                doc.get('source') or 
                                doc.get('url') or 
                                doc.get('id') or 
                                'Unknown')
                        
                        # Try different field names for title
                        title = (doc.get('title') or 
                               doc.get('filename') or 
                               doc.get('subject') or 
                               doc.get('name') or 
                               source or 
                               'Unknown Document')
                            
                        documents.append({
                            'content': content,
                            'sourceurl': source,
                            'title': title,
                            'highlights': doc.get('@search.highlights', {}),
                            'raw_doc': dict(doc)  # Keep raw doc for debugging
                        })
                    
                    print(f"Strategy {i+1} found {len(documents)} usable documents (from {total_count} total)")
                    
                    if documents:  # Return first successful search with content
                        return documents
                        
                except Exception as strategy_error:
                    print(f"Strategy {i+1} failed: {strategy_error}")
                    continue
            
            print("All search strategies failed")
            return []
            
        except Exception as e:
            print(f"Error in search_documents: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def generate_response(self, query: str, documents: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
        """Generate response using retrieved documents with improved error handling"""
        try:
            if not documents:
                yield "I couldn't find any relevant documents to answer your question. Please try rephrasing your query or ask about a different topic."
                return
                
            if not self.openai_client:
                yield "OpenAI client is not initialized. Please check the configuration."
                return
            
            # Create context from documents with better formatting
            context_parts = []
            for i, doc in enumerate(documents, 1):
                content = doc['content'][:1500]  # Increased content length
                title = doc['title']
                source = doc['sourceurl']
                
                context_parts.append(f"Document {i}:\nTitle: {title}\nSource: {source}\nContent: {content}\n")
            
            context = "\n".join(context_parts)
            
            system_message = """You are a helpful AI assistant that answers questions based on provided documents. 
            
            Guidelines:
            - Use the context provided to answer the user's question accurately
            - If the answer is not clearly in the context, say "Based on the available documents, I don't have enough information to answer that question."
            - Always cite the document sources when providing information
            - Be specific and provide detailed answers when possible
            - If multiple documents contain relevant information, synthesize the information coherently"""
            
            user_message = f"""Context from relevant documents:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context above. If you cannot answer based on the available documents, please say so clearly."""

            print(f"Generating response for query: '{query}' using {len(documents)} documents")
            
            # Stream the response with better error handling
            try:
                response = await self.openai_client.chat.completions.create(
                    model=app_settings.azure_openai.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    max_tokens=1500,  # Increased token limit
                    stream=True
                )
                
                response_chunks = 0
                async for chunk in response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        response_chunks += 1
                        yield content
                
                if response_chunks == 0:
                    yield "I received an empty response from the AI model. Please try your question again."
                else:
                    print(f"Generated response with {response_chunks} chunks")
                    
            except Exception as openai_error:
                print(f"OpenAI API error: {openai_error}")
                yield f"I encountered an error while generating the response: {str(openai_error)}. Please try again."
                    
        except Exception as e:
            print(f"Error in generate_response: {e}")
            import traceback
            traceback.print_exc()
            yield f"An unexpected error occurred: {str(e)}. Please try again."
    
    async def chat(self, query: str) -> AsyncGenerator[str, None]:
        """Main chat function with comprehensive error handling"""
        try:
            if not query or not query.strip():
                yield "Please provide a question or query."
                return
                
            query = query.strip()
            print(f"Processing chat query: '{query}'")
            
            # Check if clients are initialized
            if not self.search_client:
                yield "Search functionality is not available. Please check the Azure Search configuration."
                return
                
            if not self.openai_client:
                yield "AI response generation is not available. Please check the OpenAI configuration."
                return
            
            # Search for relevant documents
            print("Starting document search...")
            documents = await self.search_documents(query)
            print(f"Document search completed. Found {len(documents)} documents")
            
            if not documents:
                yield "I couldn't find any relevant documents to answer your question. This could be because:\n"
                yield "- The query doesn't match any content in our document index\n"
                yield "- The document search service is experiencing issues\n\n"
                yield "Please try:\n"
                yield "- Rephrasing your question with different keywords\n"
                yield "- Asking about a more general topic\n"
                yield "- Checking if your question relates to the documents in our knowledge base"
                return
            
            # Generate response
            print("Starting response generation...")
            response_generated = False
            async for chunk in self.generate_response(query, documents):
                response_generated = True
                yield chunk
            
            if not response_generated:
                yield "Failed to generate a response. Please try your question again."
                
        except Exception as e:
            print(f"Error in chat function: {e}")
            import traceback
            traceback.print_exc()
            yield f"An unexpected error occurred while processing your request: {str(e)}. Please try again."


# Global instance
simple_rag = SimpleRAG()

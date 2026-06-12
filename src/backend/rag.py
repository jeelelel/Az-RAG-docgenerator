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

from dotenv import load_dotenv
load_dotenv()


class SimpleRAG:
    def __init__(self):
        self.search_client = None
        self.openai_client = None
        self._init_clients()
    
    def _init_clients(self):
        try:
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
            
            openai_key = os.getenv("AZURE_OPENAI_KEY")
            openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            
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
        try:
            if not self.search_client:
                print("Search client not initialized")
                return []
                
            print(f"Searching for: '{query}' in index: {app_settings.datasource.index if app_settings.datasource else 'None'}")
            
            search_strategies = [
                {"search_text": query, "search_mode": "any"},
                {"search_text": query, "search_mode": "all"},
                {"search_text": f'"{query}"'},  # Exact phrase
                {"search_text": "*", "search_mode": "any"}  # Fallback to all documents
            ]
            
            for i, strategy in enumerate(search_strategies):
                try:
                    print(f"Strategy {i+1}: {strategy}")
                    
                    search_params = {
                        "top": top_k,
                        "include_total_count": True,
                        "highlight_fields": "chunk"
                    }
                    search_params.update(strategy)
                    
                    results = await self.search_client.search(**search_params)
                    
                    documents = []
                    total_count = 0
                    
                    async for doc in results:
                        total_count += 1
                        content = doc.get('chunk', '').strip()
                        if len(content) < 10:
                            continue
                        
                        source = (doc.get('sourceurl') or
                                doc.get('filename') or 
                                doc.get('filelocation') or 
                                doc.get('source') or 
                                doc.get('url') or 
                                doc.get('id') or 
                                'Unknown')
                        
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
                            'raw_doc': dict(doc)
                        })
                    
                    print(f"Strategy {i+1} found {len(documents)} usable documents (from {total_count} total)")
                    
                    if documents:
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
        try:
            if not documents:
                yield "I couldn't find any relevant documents to answer your question. Please try rephrasing your query or ask about a different topic."
                return
                
            if not self.openai_client:
                yield "OpenAI client is not initialized. Please check the configuration."
                return
            
            def tabbed_lines_to_html_table(text):
                lines = text.split('\n')
                table_rows = []
                for line in lines:
                    if '\t' in line:
                        cells = line.split('\t')
                        table_rows.append('<tr>' + ''.join(f'<td>{cell.strip()}</td>' for cell in cells) + '</tr>')
                if table_rows:
                    header = table_rows[0]
                    table_html = '<table border="1">' + header + ''.join(table_rows[1:]) + '</table>'
                    return table_html
                return None

            context_parts = []
            for i, doc in enumerate(documents, 1):
                raw_content = doc['content'][:3000]
                table_html = tabbed_lines_to_html_table(raw_content)
                if table_html:
                    content = f"[Table detected]\n{table_html}"
                else:
                    content = raw_content
                title = doc['title']
                source = doc['sourceurl']
                context_parts.append(f"Document {i}:\nTitle: {title}\nSource: {source}\nContent: {content}\n")
            context = "\n".join(context_parts)
            
            system_message = """
You are a helpful AI assistant. Your task is to generate a new report or document based on the user's prompt, using the provided previous documents as templates and examples.

Guidelines:
- Carefully analyze the structure, style, and details of the provided documents.
- Synthesize a new, original report that matches the structure and formatting of the examples, but is tailored to the user's prompt.
- Always keep the structure of the report as defined below, regardless of the user prompt or the structure of the previous documents.
- Do not copy content verbatim; instead, use the context as a guide for structure, tone, and required sections.
- If the user prompt requests a new SOW or similar document, generate all required sections, filling in details relevant to the prompt.
- Always cite sources if you use specific information from the context.
- If information is missing, make reasonable assumptions or clearly indicate where user input is needed.
- If the answer is not clearly in the context, say "Based on the available documents, I don't have enough information to answer that question."
- Be specific and provide detailed answers when possible.
- If multiple documents contain relevant information, synthesize the information coherently.
- For fee precision, try to give an estimate based on how many days will be required for the project and always give out an exact number for fees.
- If user gave budget constraints, make sure to address them in the proposal and expand the budget in a more detailed way for example if they said budget is 10 days the 2 days is for preparation and etc. if the give money budget expansion is needed, provide a detailed breakdown of how the budget will be allocated across different phases of the project.

The content must strictly be formatted as follows:
1. Executive Summary (Minimum 300 words)
2. Approach
    Explanation of Approach and Methodologies (Minimum 300 words)
    2.1 In Scope (Use ID IN01, IN02, ... and Description)
    2.2 Out of Scope (Use ID OOS01, OOS02, ... and Description)
    2.3 Deliverables (Use ID DEL01, DEL02, ... and Description)
    2.4 Assumptions (Use ID A01, A02, ... and Description)
    2.5 Dependencies (Use ID DEP01, DEP02, ... and Description)
    2.6 Risks (Use ID RIS01, RIS02, ... and Description)
3. Fees and Timings
    3.1 Fees
        3.1.1 Work Effort Estimate
        3.1.2 Cost Estimates
    3.2 Timelines
        Start Date :
        End Date :
    3.3 Synogize Personnel (Table Name and Role)
    3.4 Client Personnel (Table Name and Role)
4. Agreement (Executed by:, Synogize, Client)
    Executed by: (Sign)
    Synogize: ______________________
    Title: ______________________
    Date: _____________________

    Executed by: (Sign)

    [Client Name]
    Title: ______________________
    Date: _____________________

5. Schedule A Consulting Services Terms and Conditions (Full Version from Previous datas)
6. Schedule B Data Safeguard for Client Data (Full Version from Previous datas)
"""
            
            user_message = f"""Context from relevant documents:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context above. If you cannot answer based on the available documents, please say so clearly."""

            print(f"Generating response for query: '{query}' using {len(documents)} documents")
            
            try:
                response = await self.openai_client.chat.completions.create(
                    model=app_settings.azure_openai.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    max_tokens=5000,
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
        try:
            if not query or not query.strip():
                yield "Please provide a question or query."
                return
                
            query = query.strip()
            print(f"Processing chat query: '{query}'")
            
            if not self.search_client:
                yield "Search functionality is not available. Please check the Azure Search configuration."
                return
                
            if not self.openai_client:
                yield "AI response generation is not available. Please check the OpenAI configuration."
                return
            
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



simple_rag = SimpleRAG()

#!/usr/bin/env python3
"""
Debug Azure Search connectivity and test search
"""
import asyncio
import os
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_search_debug():
    # Load settings from environment variables
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    index_name = os.getenv("AZURE_SEARCH_INDEX", "crossmark-21july")
    key = os.getenv("AZURE_SEARCH_KEY")
    
    if not endpoint or not key:
        raise ValueError("AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY must be set in environment variables")
    
    search_client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(key)
    )
    
    try:
        print(f"Testing connection to: {endpoint}")
        print(f"Index: {index_name}")
        
        # Test search with simple query
        print("\n1. Testing search for '*' (all documents):")
        results = await search_client.search(
            search_text="*",
            top=3,
            include_total_count=True
        )
        
        count = 0
        async for doc in results:
            count += 1
            print(f"Document {count}:")
            print(f"  Keys: {list(doc.keys())}")
            if 'content' in doc:
                content = doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
                print(f"  Content: {content}")
            print(f"  Source: {doc.get('sourceurl', 'N/A')}")
            print()
        
        if count == 0:
            print("No documents found!")
        
        # Test search with specific query
        print("\n2. Testing search for 'document':")
        results = await search_client.search(
            search_text="document",
            top=3
        )
        
        count = 0
        async for doc in results:
            count += 1
            print(f"Document {count}: {doc.get('sourceurl', 'N/A')}")
        
        if count == 0:
            print("No documents found for 'document'!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await search_client.close()

if __name__ == "__main__":
    asyncio.run(test_search_debug())

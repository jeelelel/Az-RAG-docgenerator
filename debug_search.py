#!/usr/bin/env python3
"""
Debug Azure Search connectivity and test search
"""
import asyncio
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential

async def test_search_debug():
    # Use the same settings as the app
    endpoint = "https://friday4julysearch.search.windows.net"
    index_name = "crossmark-21july"
    key = "REDACTED_AZURE_SEARCH_KEY_2"
    
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

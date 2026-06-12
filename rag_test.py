import requests
import json

API_URL = "http://127.0.0.1:8000/simple_conversation"

# List of test questions for RAG
TEST_QUERIES = [
    "Summarize the main purpose of the SOW - Gordon Tafe Collaborative Advisory.pdf.",
    "Describe the process for terminating services as outlined in the SOW.",
    "What services are provided to Gordon Tafe as per the SOW?"
]

def run_rag_test():
    targeted_queries = [
        "What data safeguards does Synogize provide?",
        "What is the non-solicitation clause in the migration support agreement?",
        "Who are the parties mentioned in the SOW - Snowflake Migration Support.pdf?",
        "What technical measures are described for client data?"
    ]
    for query in targeted_queries:
        payload = {
            "messages": [
                {"role": "user", "content": query}
            ],
            "chat_type": "browse"
        }
        print(f"\n=== Query: {query} ===")
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                print(response.text)
            else:
                print(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    run_rag_test()

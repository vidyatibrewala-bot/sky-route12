import os
from openai import OpenAI

def test_config():
    os.environ["API_BASE_URL"] = "http://mock-proxy.test/v1"
    os.environ["API_KEY"] = "sk-test-key"
    
    print(f"Testing with API_BASE_URL: {os.environ['API_BASE_URL']}")
    
    client = OpenAI(
        base_url=os.environ["API_BASE_URL"],
        api_key=os.environ["API_KEY"]
    )
    
    print(f"Client base_url: {client.base_url}")
    print("Client initialized successfully.")

if __name__ == "__main__":
    test_config()

import asyncio
import os
from dotenv import load_dotenv
from llm.openai_provider import OpenAIProvider
from llm.provider import Message

async def test_deepseek():
    load_dotenv()
    print("Checking DeepSeek Integration...")
    
    # We use deepseek-chat model (assuming user wants this)
    # The provider will now auto-detect DEEPSEEK_API_KEY and use DeepSeek URL
    provider = OpenAIProvider(model="deepseek-chat")
    
    print(f"Using Client Base URL: {provider.client.base_url}")
    
    try:
        response = await provider.generate([
            Message(role="user", content="Hello, respond with 'DeepSeek is Ready!' if you receive this.")
        ])
        print("\n[RESPONSE]")
        print(response.content)
        print("\n✅ DeepSeek is connected and working!")
    except Exception as e:
        print(f"\n❌ Failed to connect to DeepSeek: {e}")
        if "api_key" in str(e).lower():
            print("Hint: Check your DEEPSEEK_API_KEY in .env file.")

if __name__ == "__main__":
    asyncio.run(test_deepseek())

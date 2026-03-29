"""Direct test of Groq API to verify the key works."""
import httpx
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def main():
    # Load env
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

    print(f"API Key: {api_key[:10]}...{api_key[-5:]}" if api_key else "NO KEY")
    print(f"Model: {model}")

    if not api_key:
        print("GROQ_API_KEY not set!")
        return

    url = "https://api.groq.com/openai/v1/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a payment analyst."},
                        {"role": "user", "content": "Say 'Groq is working' in exactly those words."},
                    ],
                    "max_tokens": 50,
                    "temperature": 0,
                },
            )
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                print(f"Response: {content}")
                print("SUCCESS - Groq API is working!")
            else:
                print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

asyncio.run(main())

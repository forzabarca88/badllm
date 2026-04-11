import logging
from pprint import pprint
import httpx
import os

logging.basicConfig(level=logging.INFO)

MODEL = 'gemma-4-e4b-it'
SYSTEM = (
    'You are a world renouned comedian - '
    'answer all conversations factually but with humor.'
)
BASE_URL = os.environ.get("BASE_URL", "http://localhost:1234/v1")

def generate_request(all_messages: list, user_message: str) -> list:
    """Keep only the last 7 messages for context management."""
    all_messages = all_messages[-7:] if all_messages else []
    all_messages.append({'role': 'user', 'content': user_message})
    return all_messages

def send_request_to_endpoint(
    client: httpx.Client,
    all_messages: list,
    instructions: str,
) -> str:
    """Send a request to the LLM endpoint and return the response."""
    response = client.post(
        BASE_URL + "/responses",
        headers={"Authorization": "Bearer doesntmatter"},
        json={
            "model": MODEL,
            "input": all_messages,
            "instructions": instructions,
            "reasoning": {"effort": "none"}
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["output"][0]["content"][0]["text"]

def chat():
    with httpx.Client() as client:
        all_messages = []
        while True:
            user_message = input("\nEnter your message: ")
            all_messages = generate_request(all_messages, user_message)
            logging.info(pprint(all_messages))

            completion = send_request_to_endpoint(client, all_messages, SYSTEM)
            print(f'\n{completion}\n')
            all_messages.append({'role': 'assistant', 'content': completion})

if __name__ == '__main__':
    chat()


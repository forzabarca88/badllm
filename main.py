import logging
from pprint import pprint
import httpx
import os

logging.basicConfig(level=logging.INFO)

MODEL='gemma-4-e4b-it'
SYSTEM=(
    'You are a world renouned comedian - '
    'answer all questions factually but with humor.')
BASE_URL = os.environ.get("BASE_URL", "http://localhost:1234/v1")


def chat():
    with httpx.Client() as client:
        all_messages = []
        while True:
            user_message = input("\nEnter your message: ")
            all_messages = generate_request(all_messages, user_message)
            logging.info(pprint(all_messages))

            response = client.post(
                BASE_URL + "/responses",
                headers={"Authorization": "Bearer doesntmatter"},
                json={
                    "model": MODEL,
                    "input": all_messages,
                    "instructions": SYSTEM,
                    "reasoning": {
                        "effort": "none"
                        }
                },
                timeout=120,
            )
            response.raise_for_status()
            completion = response.json()["output"][0]["content"][0]["text"]

            print(f'\n{completion}\n')
            all_messages.append({'role': 'assistant', 'content': completion})


def generate_request(all_messages: list, user_message: str) -> list:
    # Keep only the last 7 messages for context management
    all_messages = all_messages[-7:]
    all_messages.append({'role': 'user', 'content': user_message})
    return all_messages


if __name__ == '__main__':
    chat()


import logging
from pprint import pprint
import httpx
logging.basicConfig(level=logging.INFO)

MODEL='qwen3.5-9b'
SYSTEM=('You are a comedian with a deadpan style -answer all questions factually but with humor.')
BASE_URL='http://192.168.0.9:1234/v1/chat/completions'


def chat():
    with httpx.Client() as client:
        all_messages = [{'role': 'system', 'content': SYSTEM}]
        while True:
            user_message = input("\nEnter your message: ")
            all_messages = generate_request(all_messages, user_message)
            logging.info(pprint(all_messages))

            response = client.post(
                BASE_URL,
                headers={"Authorization": "Bearer doesntmatter"},
                json={
                    "model": MODEL,
                    "messages": all_messages
                },
                timeout=120,
            )
            response.raise_for_status()
            completion = response.json()["choices"][0]["message"]["content"]

            print(completion)
            all_messages.append({'role': 'assistant', 'content': completion})


def generate_request(all_messages, user_message):
    all_messages = all_messages[-7:]
    all_messages.append({'role': 'user', 'content': user_message})
    return all_messages


if __name__ == '__main__':
    chat()





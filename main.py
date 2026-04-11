import logging
from pprint import pprint
import httpx
logging.basicConfig(level=logging.INFO)

MODEL='qwen3.5-9b'
SYSTEM=('You are a comedian with a deadpan style -answer all questions factually but with humor.')
BASE_URL='http://jdc-media:1234/v1/chat/completions'


def chat():
    with httpx.Client() as client:
        all_messages = []
        while True:
            user_message = input("\nEnter your message: ")
            all_messages = generate_request(all_messages, user_message, SYSTEM)
            logging.info(pprint(all_messages))

            try:
                response = client.post(
                    BASE_URL,
                    json={
                        "model": MODEL,
                        "messages": all_messages
                    },
                    timeout=120
                )
                completion = response.json()["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                logging.error(f"Response parsing error: {e}")
                print("No response received from server.")
                continue

            print(completion)
            all_messages.append({'role': 'assistant', 'content': completion})


def generate_request(all_messages, user_message, system_message=SYSTEM):
    all_messages = all_messages[-7:]
    all_messages.extend(
        [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_message}
        ]
    )
    return all_messages


if __name__ == '__main__':
    chat()



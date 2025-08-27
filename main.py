import asyncio
from pprint import pprint
import logging
from ollama import AsyncClient

logging.basicConfig(level=logging.INFO)

MODEL='llama3.2'
SYSTEM='You are a comedian with a deadpan style - answer all questions factually but with humor'


async def chat(model=MODEL, system_message=SYSTEM):
    all_messages = []
    while True:
        user_message = input("\nEnter your message: ")
        all_messages = generate_request(all_messages, user_message, system_message)
        logging.info(pprint(all_messages))
        full_response = []
        async for part in await AsyncClient().chat(model=model, messages=all_messages, stream=True):
            print(part['message']['content'], end='', flush=True)
            full_response.append(part['message']['content'])
        all_messages.append({'role': 'assistant', 'content': ''.join(full_response)})


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
    asyncio.run(chat())

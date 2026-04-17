import logging
from pprint import pprint
import httpx
import os
import json

logging.basicConfig(level=logging.WARNING)

MODEL = 'qwen3.5-9b'
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
    """Send a streaming request to the LLM endpoint and return the response."""
    response_text = ""
    raw_lines_received = []
    
    try:
        with client.stream(
            "POST",
            BASE_URL + "/responses",
            headers={"Authorization": "Bearer doesntmatter", "Accept": "text/event-stream"},
            json={
                "model": MODEL,
                "input": all_messages,
                "instructions": instructions,
                "stream": True,
            },
            timeout=120,
        ) as response:
            response.raise_for_status()

            for line in response.iter_lines():
                if not line or line.startswith("event:"):
                    continue
                
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    raw_lines_received.append(repr(data_str))
                    logging.debug(f"SSE chunk: {repr(data_str)}")
                    try:
                        chunk = json.loads(data_str)
                        
                        # Handle both direct string delta and nested structure
                        if isinstance(chunk, dict):
                            text = None
                            
                            # Case 1: Direct string in "delta" field (e.g., {"delta": "Hello"})
                            if "delta" in chunk and isinstance(chunk["delta"], str):
                                text = chunk["delta"]
                            
                            # Case 2: Nested structure with "text" inside delta
                            elif "delta" in chunk and isinstance(chunk["delta"], dict) and "text" in chunk["delta"]:
                                text = chunk["delta"]["text"]
                            
                            if text is not None and chunk["type"] != "response.reasoning_text.delta":
                                print(text, end='', flush=True)
                                response_text += text
                    except (json.JSONDecodeError, KeyError, TypeError):
                        logging.warning(f"Failed to parse SSE data: {line}")
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}", exc_info=True)
    except httpx.TimeoutException as e:
        logging.error(f"Request timed out: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"Unexpected error during request: {e}", exc_info=True)
    
    if raw_lines_received:
        logging.debug(f"Total SSE chunks received: {len(raw_lines_received)}\n{raw_lines_received}")

    return response_text

def chat():
    with httpx.Client() as client:
        all_messages = []
        while True:
            user_message = input("\nEnter your message: ")
            if not user_message.strip():
                continue
            all_messages = generate_request(all_messages, user_message)
            logging.info(f"Messages before request: {all_messages}")

            print("\nAssistant: ", end='', flush=True)
            completion = send_request_to_endpoint(client, all_messages, SYSTEM)
            print()

            if not completion.strip():
                logging.warning("Received empty response from API")
            
            all_messages.append({'role': 'assistant', 'content': completion})

if __name__ == '__main__':
    chat()


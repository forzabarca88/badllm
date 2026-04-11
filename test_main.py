import unittest
from main import generate_request, MODEL, SYSTEM, BASE_URL, send_request_to_endpoint
import httpx

class TestGenerateRequest(unittest.TestCase):
    """Test cases for generate_request function."""

    def test_generate_request_basic(self):
        """Test that generate_request returns correct message structure."""
        all_messages = []
        user_message = "hello"
        
        result = generate_request(all_messages, user_message)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['role'], 'user')
        self.assertEqual(result[-1]['content'], 'hello')

    def test_generate_request_truncates_old_messages(self):
        """Test that generate_request keeps only last 7 messages."""
        # Create a long conversation history (8 messages)
        all_messages = [
            {'role': 'assistant', 'content': 'old response 1'},
            {'role': 'user', 'content': 'old user 1'},
            {'role': 'assistant', 'content': 'old response 2'},
            {'role': 'user', 'content': 'old user 2'},
            {'role': 'assistant', 'content': 'old response 3'},
            {'role': 'user', 'content': 'old user 3'},
            {'role': 'assistant', 'content': 'old response 4'},
        ]
        
        result = generate_request(all_messages, "new message")
        
        self.assertEqual(len(result), 8)  # 7 old + 1 new (truncates to last 7 then adds new)
        self.assertEqual(result[-2]['role'], 'assistant')
        self.assertEqual(result[-1]['content'], 'new message')

    def test_generate_request_with_empty_history(self):
        """Test generate_request with empty conversation history."""
        all_messages = []
        user_message = "first message"
        
        result = generate_request(all_messages, user_message)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['role'], 'user')
        self.assertEqual(result[0]['content'], 'first message')

class TestIntegration(unittest.TestCase):
    """Integration tests for the LLM endpoint."""

    def test_endpoint_hello_world(self):
        """Test that the endpoint responds to 'hello world' message."""
        with httpx.Client() as client:
            all_messages = [{"role": "user", "content": "hello world"}]
            completion = send_request_to_endpoint(client, all_messages, SYSTEM)

        self.assertGreater(len(completion), 0)  # Ensure response is non-empty
if __name__ == '__main__':
    unittest.main()


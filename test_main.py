import unittest
from main import generate_request, MODEL, SYSTEM, BASE_URL
import httpx
import os


class TestGenerateRequest(unittest.TestCase):
    """Test cases for generate_request function."""

    def test_generate_request_basic(self):
        """Test that generate_request returns correct message structure."""
        all_messages = []
        user_message = "hello"
        
        result = generate_request(all_messages, user_message, SYSTEM)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['role'], 'system')
        self.assertEqual(result[1]['role'], 'user')
        self.assertEqual(result[1]['content'], 'hello')

    def test_generate_request_truncates_old_messages(self):
        """Test that generate_request keeps only last 7 messages."""
        # Create a long conversation history
        all_messages = [
            {'role': 'assistant', 'content': 'old response 1'},
            {'role': 'user', 'content': 'old user 1'},
            {'role': 'assistant', 'content': 'old response 2'},
            {'role': 'user', 'content': 'old user 2'},
            {'role': 'assistant', 'content': 'old response 3'},
            {'role': 'user', 'content': 'old user 3'},
            {'role': 'assistant', 'content': 'old response 4'},
        ]
        
        result = generate_request(all_messages, "new message", SYSTEM)
        
        self.assertEqual(len(result), 9)  # 7 old + 2 new
        self.assertEqual(result[0]['role'], 'system')
        self.assertEqual(result[-1]['content'], 'new message')

    def test_generate_request_with_empty_history(self):
        """Test generate_request with empty conversation history."""
        all_messages = []
        user_message = "first message"
        
        result = generate_request(all_messages, user_message, SYSTEM)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['role'], 'system')
        self.assertEqual(result[1]['content'], 'first message')

    def test_model_constant(self):
        """Test that MODEL constant is set correctly."""
        self.assertEqual(MODEL, 'qwen3.5-9b')


class TestIntegration(unittest.TestCase):
    """Integration tests for the LLM endpoint."""

    @unittest.skipUnless(os.getenv('INTEGRATION_TESTS'), "INTEGRATION_TESTS not set")
    def test_endpoint_hello_world(self):
        """Test that the endpoint responds to 'hello world' message."""
        with httpx.Client() as client:
            response = client.post(
                BASE_URL,
                json={
                    "model": MODEL,
                    "messages": [
                        {'role': 'system', 'content': SYSTEM},
                        {'role': 'user', 'content': 'hello world'}
                    ],
                    "stream": False
                },
                timeout=120
            )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('choices', response_data)
        self.assertGreater(len(response_data['choices'][0]['message']['content']), 0)

import unittest
from unittest.mock import patch, MagicMock
from chat_app.services.chatbot_service import ChatbotService

class TestChatbotService(unittest.TestCase):
    def setUp(self):
        self.chatbot = ChatbotService()

    def test_train_and_conversational_data(self):
        conversation = [
            "Hello",
            "Hi there!",
            "How are you?",
            "I'm good, thanks!"
        ]
        self.chatbot.train(conversation)
        self.assertIn(("hello", "Hi there!"), self.chatbot.conversational_data)
        self.assertIn(("how are you?", "I'm good, thanks!"), self.chatbot.conversational_data)

    def test_keyword_match_response(self):
        response = self.chatbot.keyword_match_response("Hello, chatbot!")
        self.assertEqual(response, "Hi there! How can I assist you today?")
        response_none = self.chatbot.keyword_match_response("No matching keyword here")
        self.assertIsNone(response_none)

    def test_default_response(self):
        response = self.chatbot.process_query("unknown query")
        self.assertEqual(response['response'], self.chatbot.default_response)
        self.assertIsNone(response['source'])

    @patch('chat_app.services.chatbot_service.openai.ChatCompletion.create')
    def test_get_gpt_response(self, mock_create):
        mock_create.return_value = {
            'choices': [
                {'message': {'content': 'This is a GPT response'}}
            ]
        }
        self.chatbot.api_based = True
        with patch('chat_app.services.chatbot_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = 'fake-key'
            response = self.chatbot.get_gpt_response("Hello GPT")
            self.assertEqual(response, 'This is a GPT response')

    def test_process_query_keyword_fallback(self):
        # No knowledge base match, but keyword match present
        response = self.chatbot.process_query("Tell me about services")
        self.assertEqual(response['source'], 'Keyword Match')
        self.assertIn("services", response['response'].lower())

    def test_process_query_knowledge_base(self):
        # Add knowledge base entry
        self.chatbot.knowledge_base = {
            'url1': {
                'title': 'Test Page',
                'content': 'This is a test content about AI and chatbot.',
                'keywords': ['test', 'content', 'ai', 'chatbot']
            }
        }
        response = self.chatbot.process_query("Tell me about AI")
        self.assertEqual(response['source'], 'Test Page')
        self.assertIn("here's what I found", response['response'])

if __name__ == '__main__':
    unittest.main()

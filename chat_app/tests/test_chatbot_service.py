import unittest
from unittest.mock import patch
from chat_app.services.chatbot_service import ChatbotService

class TestChatbotService(unittest.TestCase):
    def setUp(self):
        self.chatbot = ChatbotService()
        # Add a sample content to knowledge base for testing content option
        self.chatbot.knowledge_base['/bba'] = {
            'title': 'BBA',
            'content': 'This is the BBA page content for testing.',
            'keywords': ['bba', 'page', 'content', 'testing']
        }
        self.chatbot.knowledge_base['/bcomca'] = {
            'title': 'BCom CA',
            'content': 'This is the BCom CA page content for testing.',
            'keywords': ['bcomca', 'page', 'content', 'testing']
        }
        self.chatbot.knowledge_base['/bcom'] = {
            'title': 'BCom',
            'content': 'This is the BCom page content for testing.',
            'keywords': ['bcom', 'page', 'content', 'testing']
        }

    def test_predefined_option_bba(self):
        response = self.chatbot.process_query('bba')
        self.assertIn('Opening the page for bba', response['response'])
        self.assertEqual(response['action'], 'open_url')
        self.assertEqual(response['url'], '/bba')

    def test_predefined_option_bcomca(self):
        response = self.chatbot.process_query('bcomca')
        self.assertIn('Opening the page for bcomca', response['response'])
        self.assertEqual(response['action'], 'open_url')
        self.assertEqual(response['url'], '/bcomca')

    def test_predefined_option_bcom(self):
        response = self.chatbot.process_query('bcom')
        self.assertIn('Opening the page for bcom', response['response'])
        self.assertEqual(response['action'], 'open_url')
        self.assertEqual(response['url'], '/bcom')

if __name__ == '__main__':
    unittest.main()

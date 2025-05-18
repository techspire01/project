import re
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from django.conf import settings
import json
import logging

# Initialize NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.knowledge_base = {}
        self.api_based = False
        self.default_response = "I'm sorry, I don't have that information yet."
        self.keyword_responses = {
            'hello': "Hi there! How can I assist you today?",
            'hey': "Hi there! How can I assist you today?",
            'hi': "Hi there! How can I assist you today?",
            'services': "We offer a variety of services including consulting, development, and support."
        }
        self.predefined_options = {
            'bba': {
                'type': 'url',
                'value': '/bba'
            },
            'bcomca': {
                'type': 'url',
                'value': '/bcomca'
            },
            'bcom': {
                'type': 'url',
                'value': '/bcom'
            }
        }
        self.conversational_data = []
        
    def train(self, conversation_list):
        """Train chatbot with a list of conversational pairs"""
        for i in range(0, len(conversation_list) - 1, 2):
            question = conversation_list[i].lower()
            answer = conversation_list[i+1]
            self.conversational_data.append((question, answer))
    
    def keyword_match_response(self, user_input):
        """Return a response based on simple keyword matching"""
        user_input_lower = user_input.lower()
        for keyword, response in self.keyword_responses.items():
            if keyword in user_input_lower:
                return response
        return None
        
    def fetch_content_from_url(self, url):
        """Fetch and parse content from a URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main content (adjust selectors based on your website structure)
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if main_content:
                # Remove script and style elements
                for script in main_content(["script", "style"]):
                    script.extract()
                
                # Get text and clean it
                text = main_content.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Store in knowledge base
                page_title = soup.title.string if soup.title else url
                self.knowledge_base[url] = {
                    'title': page_title,
                    'content': text,
                    'keywords': self.extract_keywords(text)
                }
                
                return True
            else:
                logger.warning(f"Could not find main content in {url}")
                return False
                
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            return False
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        tokens = word_tokenize(text.lower())
        keywords = [word for word in tokens if word.isalnum() and word not in self.stop_words]
        return keywords
    
    def search_knowledge_base(self, query):
        """Search the knowledge base for relevant information"""
        query_keywords = self.extract_keywords(query)
        
        best_match = None
        best_score = 0
        
        for url, data in self.knowledge_base.items():
            # Calculate simple keyword match score
            score = sum(1 for keyword in query_keywords if keyword in data['keywords'])
            
            if score > best_score:
                best_score = score
                best_match = data
        
        return best_match, best_score
    
    def get_gpt_response(self, user_input):
        """Get response from OpenAI GPT model directly"""
        try:
            import openai
            openai.api_key = settings.OPENAI_API_KEY
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_input}]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"OpenAI GPT error: {str(e)}")
            return None
    
    def process_query(self, query, base_url=None, use_live_ai=False):
        """Process user query and generate a response"""
        # Check if user is selecting a predefined option
        if query in self.predefined_options:
            option = self.predefined_options[query]
            if option['type'] == 'url':
                return {
                    'response': f"Opening the page for {query}: {option['value']}",
                    'source': 'Predefined Option',
                    'action': 'open_url',
                    'url': option['value']
                }
            elif option['type'] == 'content':
                # Fetch content from URL if not already in knowledge base
                if option['value'] not in self.knowledge_base:
                    self.fetch_content_from_url(option['value'])
                content_data = self.knowledge_base.get(option['value'], None)
                if content_data:
                    return {
                        'response': f"Here is the information about {query}: {self.summarize_content(content_data['content'], query)}",
                        'source': 'Predefined Option Content'
                    }
                else:
                    return {
                        'response': f"Sorry, I couldn't retrieve information about {query} at the moment.",
                        'source': None
                    }
        
        # If using external API (like OpenAI) or forced live AI response
        if (self.api_based or use_live_ai) and hasattr(settings, 'OPENAI_API_KEY'):
            return self.get_api_response(query)
        
        # Otherwise use our knowledge base
        best_match, score = self.search_knowledge_base(query)
        
        if best_match and score > 0:
            # Return information based on knowledge base
            return {
                'response': f"Based on {best_match['title']}, here's what I found: {self.summarize_content(best_match['content'], query)}",
                'source': best_match['title']
            }
        
        # Keyword matching fallback
        keyword_response = self.keyword_match_response(query)
        if keyword_response:
            return {
                'response': keyword_response,
                'source': 'Keyword Match'
            }
        
        elif base_url:
            # If we don't have information but have a base URL, suggest browsing
            return {
                'response': f"I don't have that information yet. You might find it on our website at {base_url}.",
                'source': None
            }
        else:
            # Generic fallback using default_response
            return {
                'response': self.default_response,
                'source': None
            }
    
    def summarize_content(self, content, query):
        """Generate a simple summary based on the query and content"""
        query_keywords = self.extract_keywords(query)
        
        # Find sentences containing keywords
        sentences = re.split(r'[.!?]', content)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in query_keywords):
                relevant_sentences.append(sentence)
        
        # Limit to 3 most relevant sentences
        if relevant_sentences:
            return " ".join(relevant_sentences[:3]) + "."
        else:
            # If no directly relevant sentences, return the first two sentences
            return " ".join([s.strip() for s in sentences[:2] if s.strip()]) + "."
    
    def get_api_response(self, query):
        """Get response from an external API like OpenAI"""
        try:
            from .api_service import openai_service
            
            # Create context from our knowledge base
            context = ""
            best_match, score = self.search_knowledge_base(query)
            
            if best_match and score > 0:
                context = f"Information from the website: {best_match['content'][:500]}..."
            
            system_message = (
                "You are a helpful assistant for a website. "
                "Answer based on the information provided when possible. "
                "If you don't have the information, be honest about it."
            )
            
            prompt = f"{context}\n\nUser question: {query}"
            
            response_text = openai_service.get_completion(prompt, system_message)
            
            if response_text:
                return {
                    'response': response_text,
                    'source': 'AI Assistant' + (f" + {best_match['title']}" if best_match else "")
                }
            else:
                return {
                    'response': "I couldn't find a good answer for that. Can you ask something else?",
                    'source': None
                }
        except Exception as e:
            logger.error(f"API error: {str(e)}")
            return {
                'response': "I'm having trouble connecting to my knowledge source right now. Please try again later.",
                'source': None
            }
    
    def enable_api_mode(self):
        """Switch to API-based responses"""
        self.api_based = True
    
    def disable_api_mode(self):
        """Switch to knowledge-base responses"""
        self.api_based = False

# Create a singleton instance
chatbot = ChatbotService()

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
    
    def process_query(self, query, base_url=None):
        """Process user query and generate a response"""
        # If using external API (like OpenAI)
        if self.api_based and hasattr(settings, 'OPENAI_API_KEY'):
            return self.get_api_response(query)
        
        # Otherwise use our knowledge base
        best_match, score = self.search_knowledge_base(query)
        
        if best_match and score > 0:
            # Return information based on knowledge base
            return {
                'response': f"Based on {best_match['title']}, here's what I found: {self.summarize_content(best_match['content'], query)}",
                'source': best_match['title']
            }
        elif base_url:
            # If we don't have information but have a base URL, suggest browsing
            return {
                'response': f"I don't have that information yet. You might find it on our website at {base_url}.",
                'source': None
            }
        else:
            # Generic fallback
            return {
                'response': "I don't have that information. Can you ask something else or be more specific?",
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
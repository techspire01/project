import os
import time
from django.core.management.base import BaseCommand
from django.contrib.sitemaps import Sitemap
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from chat_app.services.chatbot_service import chatbot
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Index website pages for the chatbot'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, help='Base URL to start crawling')
        parser.add_argument('--depth', type=int, default=2, help='Crawl depth')
        parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds')
        parser.add_argument('--limit', type=int, default=20, help='Maximum number of pages to index')

    def handle(self, *args, **options):
        base_url = options['url']
        depth = options['depth']
        delay = options['delay']
        limit = options['limit']
        
        if not base_url:
            self.stderr.write(self.style.ERROR('Please provide a base URL'))
            return
        
        # Normalize base URL
        parsed_url = urlparse(base_url)
        if not parsed_url.scheme:
            base_url = 'http://' + base_url
        
        self.stdout.write(self.style.SUCCESS(f'Starting to index {base_url} with depth {depth}'))
        
        visited = set()
        to_visit = [(base_url, 0)]  # (url, depth)
        indexed_count = 0
        
        while to_visit and indexed_count < limit:
            current_url, current_depth = to_visit.pop(0)
            
            if current_url in visited:
                continue
                
            visited.add(current_url)
            
            self.stdout.write(f'Indexing: {current_url}')
            success = chatbot.fetch_content_from_url(current_url)
            
            if success:
                indexed_count += 1
                self.stdout.write(self.style.SUCCESS(f'Successfully indexed ({indexed_count}/{limit}): {current_url}'))
            else:
                self.stdout.write(self.style.WARNING(f'Failed to index: {current_url}'))
            
            if current_depth < depth:
                # Find more links on this page
                try:
                    response = requests.get(current_url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(current_url, href)
                        
                        # Skip external links, anchors, etc.
                        parsed = urlparse(full_url)
                        if not parsed.netloc or parsed.netloc == urlparse(base_url).netloc:
                            if full_url not in visited and full_url not in [u for u, _ in to_visit]:
                                to_visit.append((full_url, current_depth + 1))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error crawling {current_url}: {str(e)}'))
            
            # Respect the delay
            time.sleep(delay)
        
        self.stdout.write(self.style.SUCCESS(f'Indexing complete! Indexed {indexed_count} pages.'))

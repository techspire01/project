from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

MAILCHIMP_API_KEY = 'd1a30ab7c300384604cf3f23ae892f1d-us12'
MAILCHIMP_SERVER_PREFIX = 'us12'  # Replace with your data center (e.g., 'us21')
MAILCHIMP_LIST_ID = '8f918f472d'

@csrf_exempt
def subscribe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        url = f'https://{MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members'
        payload = {
            'email_address': email,
            'status': 'subscribed'
        }
        headers = {
            'Authorization': f'Bearer {MAILCHIMP_API_KEY}',
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code in [200, 201]:  # Success codes
            return JsonResponse({'message': 'Successfully subscribed'})
        else:
            try:
                error_details = response.json()
            except json.JSONDecodeError:
                error_details = {'error': 'Unknown error occurred'}
            return JsonResponse({'error': 'Failed to subscribe', 'details': error_details}, status=response.status_code)

@csrf_exempt

def contact_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')

        # Mailchimp settings
        api_key = settings.MAILCHIMP_API_KEY
        server_prefix = api_key.split('-')[-1]
        list_id = settings.MAILCHIMP_LIST_ID

        url = f'https://{server_prefix}.api.mailchimp.com/3.0/lists/{list_id}/members'

        data = {
            "email_address": email,
            "status": "subscribed",
            "merge_fields": {
                "FNAME": full_name,
                "LNAME": last_name,
                "PHONE": mobile_number
            }
        }

        response = requests.post(
            url,
            auth=("anystring", api_key),
            json=data
        )

        if response.status_code == 200 or response.status_code == 204:
            return render(request, 'contact.html', {"message": "Successfully submitted"})
        else:
            return render(request, 'contact.html', {"error": "Failed to submit. Please try again with different mail_id."})

    return render(request, 'contact.html')




# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request): 
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def bba(request):
    return render(request, 'bba.html')
def login(request):
    return render(request, 'login.html')
def AIML(request):  
    return render(request, 'AIML.html')
def Cloud(request):
    return render(request, 'Cloud.html')

def bcom(request):
    return render(request, 'bcom.html')

def be_ece(request):
    return render(request, 'be-ece.html')

def bsc_it(request):
    return render(request, 'bscIT.html')

def data_analyst(request):
    return render(request, 'data analyst.html')

def web_developer(request):
    return render(request, 'Web developer.html')

def be_it(request):
    return render(request, 'BE it.html')

def bsc_cs(request):
    return render(request, 'BSc CS.html')

def bcomca(request):
    return render(request, 'bcomca.html')

def be_eee(request):
    return render(request, 'BE EEE.html')

def detail_page(request):
    return render(request, 'detail-page.html')

def listing_page(request):

    return render(request, 'listing-page.html')

def small(request):
    return render(request, 'small.html')



import os
import re
from django.conf import settings
from django.shortcuts import render
from bs4 import BeautifulSoup

import re

def strip_django_tags(html):
    # Remove Django template tags
    html = re.sub(r'{%.*?%}', '', html)
    html = re.sub(r'{{.*?}}', '', html)
    return html

'''
def extract_snippet(text, query, window=30):
    """
    Extracts a snippet around the first occurrence of the query word, ensuring words aren't cut off.
    """
    matches = list(re.finditer(re.escape(query), text, re.IGNORECASE))
    if not matches:
        return ''
    
    match = matches[0]
    start = max(match.start() - window, 0)
    end = min(match.end() + window, len(text))

    # Expand to nearest whitespace
    while start > 0 and text[start] not in ' \n\t':
        start -= 1
    while end < len(text) and text[end - 1] not in ' \n\t':
        end += 1

    snippet = text[start:end].strip()
    return snippet'''

def extract_snippet(text, query):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sentence in sentences:
        if re.search(re.escape(query), sentence, re.IGNORECASE):
            return sentence.strip()
    return ''
import re



def clean_html_text(html):
    html = strip_django_tags(html)
    soup = BeautifulSoup(html, 'html.parser')

    # Remove irrelevant tags
    for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav']):
        tag.decompose()

    # Focus on main content areas
    main_content = soup.find(['main', 'article', 'section'])
    text = main_content.get_text(separator=' ', strip=True) if main_content else soup.get_text(separator=' ', strip=True)
    return text


def search(request):
    query = request.GET.get('search', '').strip()
    results = []

    if query:
        templates_dir = os.path.join(settings.BASE_DIR, 'project', 'templates')
        for filename in os.listdir(templates_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(templates_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    cleaned_text = clean_html_text(html_content)

                    if re.search(re.escape(query), cleaned_text, re.IGNORECASE):
                        snippet = extract_snippet(cleaned_text, query)
                        results.append({
                            'filename': filename[:-5],  # remove .html
                            'snippet': snippet,
                            'url': f'/{filename[:-5]}'
                        })

    return render(request, 'search_results.html', {'query': query, 'results': results})

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json

MAILCHIMP_API_KEY = 'your-mailchimp-api-key'
MAILCHIMP_SERVER_PREFIX = 'your-server-prefix'  # e.g., 'us21'
MAILCHIMP_LIST_ID = 'your-audience-list-id'

@csrf_exempt
def add_to_mailchimp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            full_name = data.get('full-name')
            company = data.get('company')
            message = data.get('message')

            if not email or not full_name:
                return JsonResponse({'error': 'Email and Full Name are required'}, status=400)

            url = f'https://{MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members'
            headers = {
                'Authorization': f'Bearer {MAILCHIMP_API_KEY}',
                'Content-Type': 'application/json',
            }
            payload = {
                'email_address': email,
                'status': 'subscribed',
                'merge_fields': {
                    'FNAME': full_name,
                    'COMPANY': company,
                    'MESSAGE': message,
                },
            }

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return JsonResponse({'message': 'Successfully added to Mailchimp'})
            else:
                return JsonResponse({'error': response.json()}, status=response.status_code)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
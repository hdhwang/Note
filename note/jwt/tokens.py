import json

import requests
from django.conf import settings

base_url = getattr(settings, 'JWT_BASE_URL')

def get_token(request):
    data = {}
    for key, value in request.POST.items():
        data[key] = value 
    headers = {"Content-Type": "application/json"}
    return requests.post(base_url, data=json.dumps(data), headers=headers, verify=False)

def refresh_token(token):
    headers = {"Content-Type": "application/json"}
    return requests.post(f"{base_url}/refresh", data=json.dumps({'refresh': token}), headers=headers, verify=False)

def verify_token(token):
    headers = {"Content-Type": "application/json"}
    return requests.post(f"{base_url}/verify", data=json.dumps({'token': token}), headers=headers, verify=False)
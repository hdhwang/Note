from django.conf import settings

import json
import requests


def get_jwt_base_url():
    return getattr(settings, "JWT_BASE_URL")

def get_access_token(request):
    return request.COOKIES.get('access')

def get_refresh_token(request):
    return request.COOKIES.get('refresh')

def get_token(request):
    data = {}
    for key, value in request.POST.items():
        data[key] = value 
    headers = {"Content-Type": "application/json"}
    return requests.post(f"{get_jwt_base_url()}", data=json.dumps(data), headers=headers, verify=False)

def refresh_token(token):
    headers = {"Content-Type": "application/json"}
    return requests.post(f"{get_jwt_base_url()}/refresh", data=json.dumps({'refresh': token}), headers=headers, verify=False)

def verify_token(token):
    headers = {"Content-Type": "application/json"}
    return requests.post(f"{get_jwt_base_url()}/verify", data=json.dumps({'token': token}), headers=headers, verify=False)
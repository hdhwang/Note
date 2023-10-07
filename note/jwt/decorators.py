from django.shortcuts import redirect
from .tokens import get_access_token, get_refresh_token

def jwt_decorator(func):
    def wrapper(request, *args, **kwargs):
        access_token = get_access_token(request)
        refresh_token = get_refresh_token(request)
        if not access_token or not refresh_token:
            return redirect('/')
            
        kwargs['access_token'] = access_token
        kwargs['refresh_token'] = refresh_token
        return func(request, *args, **kwargs)

    return wrapper
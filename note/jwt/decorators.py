from django.shortcuts import redirect

from note.jwt.tokens import verify_token


def access_token_required(func):
    def wrapper(request, *args, **kwargs):
        access_token = request.COOKIES.get('access')
        if not access_token:
            return redirect('/')
        kwargs['access_token'] = access_token
        return func(request, *args, **kwargs)

    return wrapper

def access_token_verified(func):
    def wrapper(request, *args, **kwargs):
        access_token = request.COOKIES.get('access')
        if not access_token:
            return redirect('/')

        data = {}
        verify_response = verify_token(access_token)
        if verify_response.status_code == 200 and verify_response.json():
            if verify_response.json().get('user'):
                data = verify_response.json().get('user')
        else:
            return redirect('/')

        kwargs['access_token'] = access_token
        kwargs['user'] = data
        
        return func(request, *args, **kwargs)

    return wrapper
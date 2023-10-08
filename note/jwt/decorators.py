from django.shortcuts import redirect

def jwt_decorator(func):
    def wrapper(request, *args, **kwargs):
        access_token = request.COOKIES.get('access')
        if not access_token:
            return redirect('/')
            
        kwargs['access_token'] = access_token
        return func(request, *args, **kwargs)

    return wrapper
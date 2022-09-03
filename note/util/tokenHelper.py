from note.util.formatHelper import *
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

import logging
logger = logging.getLogger(__name__)


def get_user_token(request):
    return to_str(Token.objects.get_or_create(user=request.user)[0])
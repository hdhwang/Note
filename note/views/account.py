import json
import logging

import requests
from django.conf import settings
from django.http import HttpResponse
from django.http.multipartparser import MultiPartParser
from django.views.generic import TemplateView, View

logger = logging.getLogger(__name__)


class AccountView(TemplateView):
    template_name = "note/account/account.html"
    context = {}

    def get(self, request, *args, **kwargs):
        self.context['user'] = kwargs.get('user')
        return self.render_to_response(self.context)


class AccountAPIView(View):
    base_url = getattr(settings, "API_BASE_URL")
    sub_path = "account/user"

    def put(self, request, *args, **kwargs):
        try:
            # put data 파싱
            put_data = MultiPartParser(
                request.META, request, request.upload_handlers
            ).parse()[0]
            data = {}
            for key, value in put_data.items():
                data[key] = value
            headers = {
                "Authorization": f"Bearer {kwargs.get('access_token')}",
                "Content-Type": "application/json",
            }
            response = requests.put(
                f"{self.base_url}/{self.sub_path}",
                data=json.dumps(data),
                headers=headers,
                verify=False,
            )
            response = HttpResponse(status=response.status_code)
            if response.status_code == 200:
                response.delete_cookie('access')
                response.delete_cookie('refresh')
                response.delete_cookie('access_exp')
                response.delete_cookie('refresh_exp')
            return response

        except Exception as e:
            logger.warning(f"[AccountAPIView - put] {str(e)}")
            return HttpResponse(status=400)
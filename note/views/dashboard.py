import logging

import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View

logger = logging.getLogger(__name__)


# 대시보드
class DashboardView(TemplateView):
    template_name = "note/dashboard.html"
    context = {}

    def get(self, request, *args, **kwargs):
        self.context['user'] = kwargs.get('user')
        return self.render_to_response(self.context)


class CountAPIView(View):
    base_url = getattr(settings, "API_BASE_URL")
    sub_path = ""

    def get(self, request, *args, **kwargs):
        try:
            headers = {
                "Authorization": f"Bearer {kwargs.get('access_token')}",
                "Content-Type": "application/json",
            }
            params = {"page_size": 1}
            response = requests.get(
                f"{self.base_url}/{self.sub_path}",
                params=params,
                headers=headers,
                verify=False,
            )
            if response.status_code == 200 and response.json():
                count = response.json().get("count")
                return JsonResponse({"count": count})
            return HttpResponse(status=response.status_code)

        except Exception as e:
            logger.warning(f"[CountAPI - get] {str(e)}")
            return HttpResponse(status=400)


# 계좌번호 수 조회
class BankAccountCntAPI(CountAPIView):
    sub_path = "bank-account"


# 시리얼 번호 수 조회
class SerialCntAPI(CountAPIView):
    sub_path = "serial"


# 노트 수 조회
class NoteCntAPI(CountAPIView):
    sub_path = "note"


# 결혼식 방명록 조회
class GuestBookCntAPI(CountAPIView):
    sub_path = "guest-book"

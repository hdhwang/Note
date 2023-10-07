from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
from note.views.views import get_access_token, get_refresh_token

import logging
import requests

logger = logging.getLogger(__name__)


# 대시보드
class DashboardView(TemplateView):
    template_name = "note/dashboard.html"
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class CountAPIView(View):
    jwt_base_url = getattr(settings, "JWT_BASE_URL")
    api_base_url = getattr(settings, "API_BASE_URL")
    api_sub_path = ""

    def get(self, request):
        try:
            access_token = get_access_token(request)
            refresh_token = get_refresh_token(request)
            if not access_token:
                return HttpResponse(status=401)

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            params = {"page_size": 1}
            response = requests.get(
                f"{self.api_base_url}/{self.api_sub_path}",
                params=params,
                headers=headers,
                verify=False,
            )
            if response.status_code == 200 and response.json():
                count = response.json().get("count")
                return JsonResponse({"count": count})
                
            # 토큰이 만료된 경우 토큰 refresh 수행
            elif response.status_code == 401 and refresh_token:
                data = {'refresh': refresh_token}
                response = requests.post(f"{self.jwt_base_url}/refresh", data=json.dumps(data), headers=headers, verify=False)

                if response.status_code == 200:
                    access = response.json().get('access')
                    refresh = response.json().get('refresh')
                    
                    response = JsonResponse({"count": count})
                    response.set_cookie('access', access)
                    response.set_cookie('refresh', refresh)
                    return response
                else:
                    return HttpResponse(status=response.status_code)
            else:
                return HttpResponse(status=response.status_code)

        except Exception as e:
            logger.warning(f"[CountAPI - get] {str(e)}")
            return HttpResponse(status=400)


# 계좌번호 수 조회
class BankAccountCntAPI(CountAPIView):
    api_sub_path = "bank-account"


# 시리얼 번호 수 조회
class SerialCntAPI(CountAPIView):
    api_sub_path = "serial"


# 노트 수 조회
class NoteCntAPI(CountAPIView):
    api_sub_path = "note"


# 결혼식 방명록 조회
class GuestBookCntAPI(CountAPIView):
    api_sub_path = "guest-book"

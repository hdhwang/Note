from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
from note.jwt.tokens import get_access_token, get_refresh_token, req_refresh_token

import logging
import requests

logger = logging.getLogger(__name__)

base_url = getattr(settings, "API_BASE_URL")
sub_path = "lotto"


class LottoView(TemplateView):
    template_name = "note/lotto.html"
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class LottoAPI(View):
    base_url = getattr(settings, "API_BASE_URL")
    sub_path = ""

    def get(self, request, *args, **kwargs):
        draw = ""

        try:
            # LIMIT 및 필터 설정
            for param in request.GET.items():
                key = param[0]
                value = param[1]

                # XSS 방지를 위한 파라미터
                if key == "draw":
                    draw = value
            
            headers = {
                "Authorization": f"Bearer {kwargs.get('access_token')}",
                "Content-Type": "application/json",
            }
            response = requests.get(f"{base_url}/{sub_path}", headers=headers, verify=False)
            if response.status_code == 200 and response.json():
                data = response.json()
                total = len(response.json())

            # 토큰이 만료된 경우 토큰 refresh 수행
            elif response.status_code == 401:
                refresh_token_response = req_refresh_token(kwargs.get('refresh_token'))
                if refresh_token_response.status_code == 200:
                    access_token = refresh_token_response.json().get('access')
                    refresh_token = refresh_token_response.json().get('refresh')
                    headers["Authorization"] = f"Bearer {access_token}"
                    response = requests.get(f"{base_url}/{sub_path}", headers=headers, verify=False)
                    if response.status_code == 200 and response.json():
                        data = response.json().get("results")
                        count = response.json().get("count")

                        response = JsonResponse(
                            {
                                "draw": draw,
                                "recordsTotal": count,
                                "recordsFiltered": count,
                                "data": data,
                            }
                        )
                        response.set_cookie('access', access_token)
                        response.set_cookie('refresh', refresh_token)
                        return response
                else:
                    return HttpResponseRedirect("/")

            return JsonResponse(
                {
                    "draw": draw,
                    "recordsTotal": total,
                    "recordsFiltered": total,
                    "data": data,
                }
            )

        except Exception as e:
            logger.warning(f"[LottoAPI - get] {str(e)}")
            return HttpResponse(status=400)

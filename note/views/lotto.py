from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
from note.views.views import get_access_token, get_refresh_token

import logging
import requests

logger = logging.getLogger(__name__)

api_base_url = getattr(settings, "API_BASE_URL")
api_sub_path = "lotto"


class LottoView(TemplateView):
    template_name = "note/lotto.html"
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class LottoAPI(View):
    jwt_base_url = getattr(settings, "JWT_BASE_URL")
    api_base_url = getattr(settings, "API_BASE_URL")
    api_sub_path = ""

    def get(self, request):
        draw = ""

        try:
            # LIMIT 및 필터 설정
            for param in request.GET.items():
                key = param[0]
                value = param[1]

                # XSS 방지를 위한 파라미터
                if key == "draw":
                    draw = value
            
            access_token = get_access_token(request)
            refresh_token = get_refresh_token(request)
            if not access_token:
                return HttpResponseRedirect("/")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
            response = requests.get(f"{api_base_url}/{api_sub_path}", headers=headers, verify=False)
            if response.status_code == 200 and response.json():
                data = response.json()
                total = len(response.json())

            # 토큰이 만료된 경우 토큰 refresh 수행
            elif response.status_code == 401 and refresh_token:
                token_refresh_data = {'refresh': refresh_token}
                refresh_token_response = requests.post(f"{self.jwt_base_url}/refresh", data=json.dumps(token_refresh_data), headers=headers, verify=False)

                if refresh_token_response.status_code == 200:
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
                        response.set_cookie('access', refresh_token_response.json().get('access'))
                        response.set_cookie('refresh', refresh_token_response.json().get('refresh'))
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

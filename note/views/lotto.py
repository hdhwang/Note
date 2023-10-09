from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View

import logging
import requests

logger = logging.getLogger(__name__)

base_url = getattr(settings, "API_BASE_URL")
sub_path = "lotto"


class LottoView(TemplateView):
    template_name = "note/lotto.html"
    context = {}

    def get(self, request, *args, **kwargs):
        self.context['user'] = kwargs.get('user')
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

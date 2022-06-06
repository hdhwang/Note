from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
from note import models
from note.util.formatHelper import *

import logging
logger = logging.getLogger(__name__)


# 대시보드
class DashboardView(TemplateView):
    template_name = 'note/dashboard.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


# 계좌번호 수 조회
class BankAccountCntAPI(View):
    def get(self, request):
        try:
            return JsonResponse({'count': models.BankAccount.objects.filter().count()})

        except Exception as e:
            logger.warning(f'[BankAccountCntAPI - get] {to_str(e)}')
            return HttpResponse(status=400)


# 시리얼 번호 수 조회
class SerialCntAPI(View):
    def get(self, request):
        try:
            return JsonResponse({'count': models.Serial.objects.filter().count()})

        except Exception as e:
            logger.warning(f'[SerialCntAPI - get] {to_str(e)}')
            return HttpResponse(status=400)


# 노트 수 조회
class NoteCntAPI(View):
    def get(self, request):
        try:
            return JsonResponse({'count': models.Note.objects.filter().count()})

        except Exception as e:
            logger.warning(f'[NoteCntAPI - get] {to_str(e)}')
            return HttpResponse(status=400)


# 결혼식 방명록 조회
class GuestBookCntAPI(View):
    def get(self, request):
        try:
            return JsonResponse({'count': models.GuestBook.objects.filter().count()})

        except Exception as e:
            logger.warning(f'[GuestBookCntAPI - get] {to_str(e)}')
            return HttpResponse(status=400)

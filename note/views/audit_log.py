from django.http import HttpResponse
from django.views.generic import TemplateView
from note.views.views import TableAPIView


# 감사 로그
class AuditLogView(TemplateView):
    template_name = 'note/audit-log.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class AuditLogAPI(TableAPIView):
    sub_path = 'audit-log'

    def post(self, request):
        HttpResponse(status=405)

    def put(self, request):
        HttpResponse(status=405)

    def delete(self, request):
        HttpResponse(status=405)
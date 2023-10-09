from django.views.generic import TemplateView
from note.views.views import TableAPIView


# 시리얼 번호 관리
class SerialView(TemplateView):
    template_name = "note/serial.html"
    context = {}

    def get(self, request, *args, **kwargs):
        self.context['user'] = kwargs.get('user')
        return self.render_to_response(self.context)


class SerialAPI(TableAPIView):
    sub_path = "serial"

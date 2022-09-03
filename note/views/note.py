from django.views.generic import TemplateView
from note.views.views import TableAPIView

# 노트
class NoteView(TemplateView):
    template_name = 'note/note.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class NoteAPI(TableAPIView):
    sub_path = 'note'
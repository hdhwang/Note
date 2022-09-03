from django.views.generic import TemplateView
from note.views.views import TableAPIView


# 결혼식 방명록
class GuestBookView(TemplateView):
    template_name = 'note/guest_book.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class GuestBookAPI(TableAPIView):
    sub_path = 'guest-book'
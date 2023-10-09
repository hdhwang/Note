from django.views.generic import TemplateView


class AccountView(TemplateView):
    template_name = "note/account/account.html"
    context = {}

    def get(self, request, *args, **kwargs):
        self.context['user'] = kwargs.get('user')
        return self.render_to_response(self.context)
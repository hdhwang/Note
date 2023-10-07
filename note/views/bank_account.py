from django.views.generic import TemplateView
from note.views.views import TableAPIView


# 계좌번호 관리
class BankAccountView(TemplateView):
    template_name = "note/bank_account.html"
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class BankAccountAPI(TableAPIView):
    sub_path = "bank-account"

from django.urls import path
from django.views.generic.base import RedirectView
from note.jwt.decorators import access_token_required, access_token_verified

from note.views import (
    views,
    audit_log,
    dashboard,
    serial,
    bank_account,
    note,
    lotto,
    guest_book,
    account,
)

urlpatterns = [
    # 로그인 관련 URL (로그인, 로그아웃)
    path("", views.IndexView.as_view(), name="index"),
    path("400", views.error_400, name="error_400"),
    path("401", views.error_401, name="error_401"),
    path("403", views.error_403, name="error_403"),
    path("404", views.error_404, name="error_404"),
    path("500", views.error_500, name="error_500"),
    path("login", views.LoginView.as_view(), name="login"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("refresh-token", views.RefreshTokenView.as_view(), name="refresh-token"),
    
    # favicon
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.ico", permanent=True)),
    
    # DataTables 한국어 json
    path("data-tables/korean", views.DataTablesKoreanView.as_view()),
    
    # 대시보드
    path("dashboard", access_token_verified(dashboard.DashboardView.as_view()), name="dashboard"),
    path("dashboard/api/bank-account", access_token_required(dashboard.BankAccountCntAPI.as_view())),
    path("dashboard/api/serial", access_token_required(dashboard.SerialCntAPI.as_view())),
    path("dashboard/api/note", access_token_required(dashboard.NoteCntAPI.as_view())),
    path("dashboard/api/guest-book", access_token_required(dashboard.GuestBookCntAPI.as_view())),
    
    # 계좌번호 관리
    path("bank-account", access_token_verified(bank_account.BankAccountView.as_view()), name="bank_account"),
    path("bank-account/api", access_token_required(bank_account.BankAccountAPI.as_view())),
    path("bank-account/api/<int:req_id>", access_token_required(bank_account.BankAccountAPI.as_view())),
    
    # 시리얼 번호 관리
    path("serial", access_token_verified(serial.SerialView.as_view()), name="serial"),
    path("serial/api", access_token_required(serial.SerialAPI.as_view())),
    path("serial/api/<int:req_id>", access_token_required(serial.SerialAPI.as_view())),
    
    # 노트 관리
    path("note", access_token_verified(note.NoteView.as_view()), name="note"),
    path("note/api", access_token_required(note.NoteAPI.as_view())),
    path("note/api/<int:req_id>", access_token_required(note.NoteAPI.as_view())),
    
    # 결혼식 방명록
    path("guest-book", access_token_verified(guest_book.GuestBookView.as_view()), name="guest_book"),
    path("guest-book/api", access_token_required(guest_book.GuestBookAPI.as_view())),
    path("guest-book/api/<int:req_id>", access_token_required(guest_book.GuestBookAPI.as_view())),
    
    # 로또 생성기
    path("lotto", access_token_verified(lotto.LottoView.as_view()), name="lotto"),
    path("lotto/api", access_token_required(lotto.LottoAPI.as_view())),
    
    # 감사 로그
    path("audit-log", access_token_verified(audit_log.AuditLogView.as_view()), name="audit_log"),
    path("audit-log/api", access_token_required(audit_log.AuditLogAPI.as_view())),

    # 계정 관리
    path("account", access_token_verified(account.AccountView.as_view()), name="account",),
    path("account/api", access_token_required(account.AccountAPIView.as_view())),
]

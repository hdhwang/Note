from django.contrib.auth import views as auth_view
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic.base import RedirectView

from note.views import views, audit_log, account, dashboard, serial, bank_account, note, lotto, guest_book

urlpatterns = [
    # 로그인 관련 URL (로그인, 로그아웃)
    path('', views.IndexView.as_view(), name='index'),
    path('error_login', views.ErrorLoginView.as_view(), name='error_login'),
    path('400', views.error_400, name='error_400'),
    path('401', views.error_401, name='error_401'),
    path('403', views.error_403, name='error_403'),
    path('404', views.error_404, name='error_404'),
    path('500', views.error_500, name='error_500'),
    path('login', views.NoteLoginView.as_view(), name='login'),
    path('logout/', views.NoteLogoutView.as_view(), name='logout'),

    # favicon
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),

    # note 관련 URL

    # DataTables 한국어 json
    path('data-tables/korean', login_required(views.DataTablesKoreanView.as_view())),

    # 대시보드
    path('dashboard', login_required(dashboard.DashboardView.as_view()), name='dashboard'),
    path('dashboard/api/bank-account', login_required(dashboard.BankAccountCntAPI.as_view())),
    path('dashboard/api/serial', login_required(dashboard.SerialCntAPI.as_view())),
    path('dashboard/api/note', login_required(dashboard.NoteCntAPI.as_view())),
    path('dashboard/api/guest-book', login_required(dashboard.GuestBookCntAPI.as_view())),

    # 계좌번호 관리
    path('bank-account', login_required(bank_account.BankAccountView.as_view()), name='bank_account'),
    path('bank-account/api', login_required(bank_account.BankAccountAPI.as_view())),
    path('bank-account/api/<int:req_id>', login_required(bank_account.BankAccountAPI.as_view())),

    # 시리얼 번호 관리
    path('serial', login_required(serial.SerialView.as_view()), name='serial'),
    path('serial/api', login_required(serial.SerialAPI.as_view())),
    path('serial/api/<int:req_id>', login_required(serial.SerialAPI.as_view())),

    # 노트 관리
    path('note', login_required(note.NoteView.as_view()), name='note'),
    path('note/api', login_required(note.NoteAPI.as_view())),
    path('note/api/<int:req_id>', login_required(note.NoteAPI.as_view())),

    # 결혼식 방명록
    path('guest-book', login_required(guest_book.GuestBookView.as_view()), name='guest_book'),
    path('guest-book/api', login_required(guest_book.GuestBookAPI.as_view())),
    path('guest-book/api/<int:req_id>', login_required(guest_book.GuestBookAPI.as_view())),

    # 로또 생성기
    path('lotto', login_required(lotto.LottoView.as_view()), name='lotto'),
    path('lotto/api', login_required(lotto.LottoAPI.as_view())),

    # 감사 로그
    path('audit-log', login_required(audit_log.AuditLogView.as_view()), name='audit_log'),
    path('audit-log/api', login_required(audit_log.AuditLogAPI.as_view())),

    # 계정 관리
    path('account/', login_required(auth_view.PasswordChangeView.as_view(template_name='note/account/account.html')), name='account'),
    path('password-change-done/', login_required(account.PasswordChangeDoneView.as_view()), name='password_change_done'),

    # 계정 관리 (관리자 전용)
    path('account/users', login_required(account.UsersView.as_view()), name='account_users'),
    path('account/users/api', login_required(account.UsersAPI.as_view())),
    path('account/users/api/<int:req_id>', login_required(account.UsersAPI.as_view())),
    path('account/users/check/<str:username>', login_required(account.CheckUserAPI.as_view())),
]

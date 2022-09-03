from axes.models import AccessAttempt
from django.shortcuts import HttpResponseRedirect, render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib import auth
from django.http import JsonResponse, HttpResponse
from django.http.multipartparser import MultiPartParser
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout as auth_logout
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate
from django.conf import settings
from django.views.generic import TemplateView, View
from note.util.dicHelper import get_dic_value
from note.util.formatHelper import *
from note.util.logHelper import insert_audit_log
from note.util.networkHelper import get_client_ip
from note.util.regexHelper import *
from note.util.tokenHelper import get_user_token


import logging
import math
import requests
import json
logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = 'note/index.html'
    context = {}

    def get(self, request, *args, **kwargs):
        # 로그인 세션이 존재하는 경우 대시보드로 이동
        if request.user.is_authenticated:
            return HttpResponseRedirect('/dashboard')

        return self.render_to_response(self.context)


# 로그인
class NoteLoginView(View):
    # 비밀번호 카운트 초기화 수행 (IP 기준)
    def axes_reset_by_ip(self, request):
        for obj in AccessAttempt.objects.all():
            if obj.ip_address == get_client_ip(request):
                obj.delete()

    def post(self, request):
        try:
            username = get_dic_value(request.POST, 'user-id')
            password = get_dic_value(request.POST, 'user-password')

            # 일치하는 사용자 계정이 존재하는 경우
            if User.objects.values().filter(username=username) \
                    and check_password(password, User.objects.get(username=username).password):

                # 활성 계정인 경우 사용자 인증 수행
                if User.objects.get(username=username).is_active:
                    user = authenticate(request, username=username, password=password)

                    # 사용자 인증에 성공한 경우
                    if user is not None:
                        sessions_list = Session.objects.all()

                        for session in sessions_list:
                            # 사용자 세션이 존재하는 경우
                            if session.get_decoded().get('_auth_user_id') == to_str(user.id):
                                user_confirm = get_dic_value(request.POST, 'user-confirm', 'N')

                                # 만료된 세션이거나 사용자가 컨펌 모달에서 확인을 클릭한 경우
                                if session.expire_date < datetime.now() or user_confirm.upper() == 'Y':
                                    session.delete()

                                # 사용자 확인이 필요한 경우 리턴
                                elif user_confirm.upper() == 'N':
                                    return JsonResponse({'data': 2})

                        # 로그인 수행
                        auth.login(request, user)

                        # 로그인 성공 감사 로그 기록
                        insert_audit_log(user.id, request, '계정', '로그인', '사용자 로그인', True)
                        return JsonResponse({'data': 1})

                    # 사용자 인증에 실패한 경우
                    else:
                        action = f'아이디 또는 비밀번호 불일치 (아이디 : {username})'
                        insert_audit_log(None, request, '계정', '로그인', action, False)

                        return JsonResponse({'data': 0})

                # 비활성 계정인 경우
                else:
                    action = f'비활성 계정 로그인 시도 (아이디 : {username})'
                    insert_audit_log(None, request, '계정', '로그인', action, False)

                    # 비밀번호 카운트 초기화 수행 (IP 기준)
                    self.axes_reset_by_ip(request)

                    return JsonResponse({'data': -1})

            # 일치하는 사용자 계정이 존재하지 않는 경우
            else:
                action = f'아이디 또는 비밀번호 불일치 (아이디 : {username})'
                insert_audit_log(None, request, '계정', '로그인', action, False)

                # 비밀번호 카운트 증가를 위해 인증 시도
                authenticate(request, username=username, password=password)

                return JsonResponse({'data': 0})

        except Exception as e:
            logger.warning(f'[login] {to_str(e)}')
            return HttpResponse(status=400)


# 로그아웃
class NoteLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        user = request.user.id
        auth_logout(request)

        # 로그아웃 감사 로그 기록
        insert_audit_log(user, request, '계정', '로그아웃', '사용자 로그아웃', True)

        next_page = self.get_next_page()
        if next_page:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(next_page)
        return super().dispatch(request, *args, **kwargs)


class ErrorLoginView(View):
    def get(self, request):
        fail_limit = getattr(settings, 'AXES_FAILURE_LIMIT')
        cool_times = to_int(getattr(settings, 'AXES_COOLOFF_TIME').seconds / 60)
        msg = f'로그인 {fail_limit}회 이상 실패로 {cool_times}분간 로그인할 수 없습니다.'

        return error_401(request, msg)


# HTTP 상태 코드 400
def error_400(request, exception):
    response = render(request, 'note/error/400.html')
    response.status_code = 400

    return response


# HTTP 상태 코드 401
def error_401(request, message=''):
    response = render(request, 'note/error/401.html', {'message': message})

    return response


# HTTP 상태 코드 403
def error_403(request, exception):
    response = render(request, 'note/error/403.html')
    response.status_code = 403

    return response


# HTTP 상태 코드 404
def error_404(request, exception):
    response = render(request, 'note/error/404.html')
    response.status_code = 404

    return response


# HTTP 상태 코드 500
def error_500(request):
    response = render(request, 'note/error/500.html')
    response.status_code = 500

    return response


class DataTablesKoreanView(View):
    def get(self, request):
        s_length_menu = get_dic_value(request.GET, 's-length-menu', '페이지당 줄수')

        response = {
            'sEmptyTable': '데이터가 없습니다.',
            'sInfo': '_START_ - _END_ / _TOTAL_',
            'sInfoEmpty': '0 - 0 / 0',
            'sInfoFiltered': '(총 _MAX_ 개)',
            'sInfoPostFix': '',
            'sInfoThousands': ',',
            'sLengthMenu': f'{s_length_menu} _MENU_',
            'sLoadingRecords': '조회중...',
            'sProcessing': '처리중...',
            'sSearch': '검색:',
            'sZeroRecords': '검색 결과가 없습니다.',
            'oPaginate': {
                'sFirst': '처음',
                'sLast': '마지막',
                'sNext': '다음',
                'sPrevious': '이전'
            },
            'oAria': {
                'sSortAscending': ': 오름차순 정렬',
                'sSortDescending': ': 내림차순 정렬'
            }
        }

        return JsonResponse(response)


class TableAPIView(View):
    base_url = getattr(settings, 'API_BASE_URL')
    sub_path = ''

    def get(self, request):
        try:
            params = {}

            page = 1
            page_size = 10
            start = 0

            # LIMIT 및 필터 설정
            for param in request.GET.items():
                key = param[0]
                value = param[1]

                if key == 'start':
                    start = to_int(value) + 1

                elif key == 'length' and to_int(value) > 0:
                    page_size = to_int(value)

                # XSS 방지를 위한 파라미터
                elif key == 'draw':
                    draw = value

                # 정렬 설정
                elif key == 'order[order]':
                    req_ordering = value
                    req_order_dir = request.GET.get('order[dir]')
                    params['ordering'] = req_order_dir + req_ordering

                # 필터 설정
                elif table_filter_regex.search(key) and value != '':
                    filter_key = f'{key.split("[value]")[0]}[data]'
                    filter_name = get_dic_value(request.GET, filter_key)
                    params[filter_name] = value

            if start > 0:
                page = math.ceil(start / page_size)

            params['page'] = page
            params['page_size'] = page_size
            
            headers = {'Authorization': f'Token {get_user_token(request)}', 'Content-Type': 'application/json'}
            response = requests.get(f'{self.base_url}/{self.sub_path}', params=params, headers=headers)
            if response.status_code == 200 and response.json():
                data = response.json().get('results')
                count = response.json().get('count')

            return JsonResponse(
                {'draw': draw, 'recordsTotal': count, 'recordsFiltered': count, 'data': data})

        except Exception as e:
            logger.warning(f'[TableAPIView - get] {to_str(e)}')
            return HttpResponse(status=400)

    def post(self, request):
        try:
            data = {}

            for key, value in request.POST.items():
                data[key] = value

            headers = {'Authorization': f'Token {get_user_token(request)}', 'Content-Type': 'application/json'}
            response = requests.post(f'{self.base_url}/{self.sub_path}', data=json.dumps(data), headers=headers)

            return HttpResponse(status=response.status_code)

        except Exception as e:
            logger.warning(f'[TableAPIView - post] {to_str(e)}')
            return HttpResponse(status=400)

    def put(self, request, req_id):
        try:
            if req_id:
                # put data 파싱
                put_data = MultiPartParser(request.META, request, request.upload_handlers).parse()[0]
                data = {}

                for key, value in put_data.items():
                    data[key] = value

                headers = {'Authorization': f'Token {get_user_token(request)}', 'Content-Type': 'application/json'}
                response = requests.put(f'{self.base_url}/{self.sub_path}/{req_id}', data=json.dumps(data), headers=headers)

                return HttpResponse(status=response.status_code)

        except Exception as e:
            logger.warning(f'[TableAPIView - put] {to_str(e)}')
            return HttpResponse(status=400)

    def delete(self, request, req_id):
        try:
            if req_id:
                headers = {'Authorization': f'Token {get_user_token(request)}', 'Content-Type': 'application/json'}
                response = requests.delete(f'{self.base_url}/{self.sub_path}/{req_id}', headers=headers)

                return HttpResponse(status=response.status_code)

        except Exception as e:
            logger.warning(f'[TableAPIView - delete] {to_str(e)}')
            return HttpResponse(status=400)
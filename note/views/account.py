from django.contrib import auth
from django.contrib.auth import password_validation
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db.models import CharField, DateTimeField
from django.db.models.functions import Cast, TruncSecond
from django.http import JsonResponse, HttpResponse
from django.http.multipartparser import MultiPartParser
from django.shortcuts import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.views.generic import View, TemplateView
from note.util.logHelper import insert_audit_log
from note.util.dicHelper import get_dic_value, insert_dic_data
from note.util.mailHelper import *
from note.util.regexHelper import *
import logging
logger = logging.getLogger(__name__)


# 감사 로그 > 카테고리
category = '계정 관리'


class PasswordChangeDoneView(View):
    def get(self, request):
        # 비밀번호 변경 성공 시 로그아웃 수행
        user = request.user.id
        auth.logout(request)

        # 로그아웃 감사 로그 기록
        insert_audit_log(user, request, '계정', '로그아웃', '비밀번호 변경', 'Y')

        return HttpResponseRedirect('/dashboard')


# 계정 관리 > 사용자 관리
class UsersView(TemplateView):
    template_name = 'note/account/users.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class UsersAPI(View):
    @method_decorator(permission_required('note.view_user', raise_exception=True))
    def get(self, request):
        try:
            val = {}
            filter_params = {}
            user_id = request.user.id

            # 컬럼 리스트
            column_list = ('last_login', 'is_superuser', 'username', 'first_name', 'email', 'is_active', 'date_joined')

            # LIMIT 시작 인덱스
            limit_start = 0

            # LIMIT 종료 인덱스
            limit_end = None

            # 정렬 설정
            ordering = '-date_joined'   # 기본 값 : 일자 (최신) 기준

            # LIMIT 및 필터 설정
            for param in request.GET.items():
                key = param[0]
                value = param[1]

                # LIMIT 시작 인덱스
                if key == 'start':
                    limit_start = to_int(value)

                # LIMIT 종료 인덱스
                elif key == 'length' and to_int(value) > -1:
                    limit_end = limit_start + to_int(value)

                # XSS 방지를 위한 파라미터
                elif key == 'draw':
                    draw = value

                # 정렬 설정
                elif key == 'order[order]':
                    req_ordering = value
                    req_order_dir = request.GET.get('order[dir]')

                    if req_ordering in column_list:
                        ordering = req_order_dir + req_ordering

                # 필터 설정
                elif table_filter_regex.search(key) and value != '':
                    filter_key = f'{key.split("[value]")[0]}[data]'
                    filter_name = get_dic_value(request.GET, filter_key)

                    # _last_login가 입력된 경우 실제 필드인 date로 치환
                    if ordering == '_last_login':
                        ordering = 'last_login'

                    # _date_joined가 입력된 경우 실제 필드인 date로 치환
                    elif ordering == '_date_joined':
                        ordering = 'date_joined'

                    if filter_name == 'is_superuser':
                        insert_dic_data(filter_params, 'is_superuser', value)

                    elif filter_name == 'username':
                        insert_dic_data(filter_params, 'username__icontains', value)

                    elif filter_name == 'first_name':
                        insert_dic_data(filter_params, 'first_name__icontains', value)

                    elif filter_name == 'email':
                        insert_dic_data(filter_params, 'email__icontains', value)

                    elif filter_name == 'is_active':
                        insert_dic_data(filter_params, 'is_active', value)

            data_cols_args = ['id', 'is_superuser', 'username', 'first_name', 'email', 'is_active']
            data_cols_kwargs = dict(
                _last_login=Cast(TruncSecond('last_login', DateTimeField()), CharField()),
                _date_joined=Cast(TruncSecond('date_joined', DateTimeField()), CharField()),
            )
            val = list(User.objects.values(
                *data_cols_args, **data_cols_kwargs).filter(**filter_params).order_by(ordering)[limit_start:limit_end])

            # 전체 레코드 수 조회
            records_total = User.objects.filter(**filter_params).count()

            return JsonResponse(
                {'draw': draw, 'recordsTotal': records_total, 'recordsFiltered': records_total, 'data': val,
                 'user_id': user_id})

        except Exception as e:
            logger.warning(f'[UsersAPI - get] {to_str(e)}')
            return HttpResponse(status=400)

    @method_decorator(permission_required('note.add_user', raise_exception=True))
    def post(self, request):
        # 감사 로그 > 내용
        actions = []

        # 감사 로그 > 결과
        result = False
        try:
            username = get_dic_value(request.POST, 'username')
            password = get_dic_value(request.POST, 'password')
            is_superuser = get_dic_value(request.POST, 'is_superuser')
            first_name = get_dic_value(request.POST, 'first_name')
            email = get_dic_value(request.POST, 'email')
            is_active = get_dic_value(request.POST, 'is_active')
            
            # 비밀번호가 8자 미만이거나 120자 초과하는 경우
            if 8 > password.__len__() > 120:
                return HttpResponse(status=400)

            try:
                # 비밀번호 유효성 검증
                password_validation.validate_password(password=password)

            # 비밀번호 유효성 검증 오류 발생 시 오류 메시지 반환
            except ValidationError as e:
                logger.error(f'[users_api] {e.messages[0]}')
                return JsonResponse({'error': e.messages[0]})

            # DB에 데이터 추가
            user = User.objects.create_user(
                username=username,
                password=password,
                is_superuser=is_superuser,
                first_name=first_name,
                email=email,
                is_active=is_active,
                date_joined=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            user.save()

            # 추가 성공 시 감사 로그 > 내용에 아이디 항목 추가
            actions.append(f'[아이디] : {to_str(user.id)}')

            # 사용자 그룹 추가
            group_name = '관리자' if is_superuser == 1 else '사용자'
            group = Group.objects.get(name=group_name)
            group.user_set.add(user)
            group.save()

            result = True
            return HttpResponse(status=201)

        except Exception as e:
            logger.warning(f'[UsersAPI - post] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            user_type = '관리자' if is_superuser == '1' else '사용자'
            active = '활성' if is_active == '1' else '비활성'

            # 감사 로그 기록
            actions.append(f'[사용자 아이디] : {username}')
            actions.append(f'[유형] : {user_type}')
            actions.append(f'[이름] : {first_name}')
            actions.append(f'[이메일] : {email}')
            actions.append(f'[활성화] : {active}')
            audit_log = f"""추가 ( {', '.join(actions)} )"""

            insert_audit_log(request.user.id, request, category, '사용자 관리', audit_log, result)

    @method_decorator(permission_required('note.change_user', raise_exception=True))
    def put(self, request, req_id):
        user_id = request.user.id

        # 감사 로그 > 내용
        actions = []
        actions.append(f'[아이디] : {to_str(req_id)}')

        # 감사 로그 > 결과
        result = False
        try:
            if req_id:

                # put data 파싱
                put_data = MultiPartParser(request.META, request, request.upload_handlers).parse()[0]
                password = get_dic_value(put_data, 'password')
                is_superuser = get_dic_value(put_data, 'is_superuser')
                first_name = get_dic_value(put_data, 'first_name')
                email = get_dic_value(put_data, 'email')
                is_active = get_dic_value(put_data, 'is_active')

                # 비밀번호가 8자 미만이거나 120자 초과하는 경우
                if 8 > password.__len__() > 120:
                    return HttpResponse(status=400)

                # id 기준으로 항목 조회
                data = User.objects.get(pk=to_int(req_id))

                actions.append(f'[사용자 아이디] : {to_str(data.username)}')

                if user_id != to_int(req_id) and to_str(data.is_superuser) != is_superuser:
                    org_user_type = '관리자' if data.is_superuser == 1 else '사용자'
                    user_type = '관리자' if is_superuser == '1' else '사용자'

                    # 감사 로그 > 내용 추가
                    actions.append(f'[유형] : {org_user_type} → {user_type}')

                    # 항목 수정
                    data.is_superuser = is_superuser

                if data.first_name != first_name:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[이름] : {to_str(data.first_name)} → {first_name}')

                    # 항목 수정
                    data.first_name = first_name

                if data.email != email:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[이메일] : {to_str(data.email)} → {email}')

                    # 항목 수정
                    data.email = email

                if user_id != to_int(req_id) and to_str(data.is_active) != is_active:
                    org_active = '활성' if data.is_active == 1 else '비활성'
                    active = '활성' if is_active == '1' else '비활성'

                    # 감사 로그 > 내용 추가
                    actions.append(f'[활성화] : {org_active} → {active}')

                    # 항목 수정
                    data.is_active = is_active

                # 변경 사항 적용
                data.save()

                # 패스워드 변경
                if user_id != to_int(req_id) and password != '':
                    user = User.objects.get(pk=to_int(req_id))
                    actions.append(f'[패스워드 변경]')

                    try:
                        # 비밀번호 유효성 검증
                        password_validation.validate_password(password=password)

                        user.set_password(password)

                        # 변경 사항 적용
                        user.save()

                    # 비밀번호 유효성 검증 오류 발생 시 오류 메시지 반환
                    except ValidationError as e:
                        logger.error(f'[UsersAPI - put] {e.messages[0]}')
                        return JsonResponse({'error': e.messages[0]})

                # 기존 그룹 모두 삭제
                data.groups.clear()

                # 사용자 그룹 추가
                group_name = 'Admin' if is_superuser == 1 else 'User'
                group = Group.objects.get(name=group_name)
                group.user_set.add(data)
                group.save()
                result = True

                return HttpResponse(status=204)

        except Exception as e:
            logger.warning(f'[UsersAPI - put] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            # 감사 로그 기록
            audit_log = f"""편집 ( {', '.join(actions)} )"""
            insert_audit_log(request.user.id, request, category, '사용자 관리', audit_log, result)


class CheckUserAPI(View):
    @method_decorator(permission_required('note.view_user', raise_exception=True))
    def get(self, request, username):
        try:
            result = False
            if User.objects.filter(username=username):
                result = True

            return JsonResponse({'data': result})

        except Exception as e:
            logger.warning(f'[CheckUserAPI - get] {to_str(e)}')
            return HttpResponse(status=400)

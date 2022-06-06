from django.http import HttpResponse, JsonResponse
from django.http.multipartparser import MultiPartParser
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.views.generic import TemplateView, View
from note import models
from note.util.AESHelper import make_enc_value, get_dec_value
from note.util.dicHelper import insert_dic_data, get_dic_value
from note.util.formatHelper import *
from note.util.logHelper import insert_audit_log
from note.util.regexHelper import *

import logging
logger = logging.getLogger(__name__)

# 감사 로그 > 카테고리
category = '계좌번호 관리'


# 계좌번호 관리
class BankAccountView(TemplateView):
    template_name = 'note/bank_account.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class BankAccountAPI(View):
    @method_decorator(permission_required('note.view_bankaccount', raise_exception=True))
    def get(self, request):
        try:
            # 컬럼 리스트
            column_list = ('bank', 'account', 'account_holder', 'description')

            # 정렬 설정
            ordering = '-id'  # 기본 값 : id 기준

            # LIMIT 시작 인덱스
            limit_start = 0

            # LIMIT 종료 인덱스
            limit_end = None

            # 필터 설정
            filter_params = {}

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

                    # 은행
                    if filter_name == 'bank':
                        insert_dic_data(filter_params, 'bank__icontains', value)

                    # 계좌번호
                    elif filter_name == 'account':
                        insert_dic_data(filter_params, 'account__icontains', value)

                    # 예금주
                    elif filter_name == 'account_holder':
                        insert_dic_data(filter_params, 'account_holder__icontains', value)

                    # 설명
                    elif filter_name == 'description':
                        insert_dic_data(filter_params, 'description__icontains', value)

            data_cols_args = ['id', 'bank', 'account', 'account_holder', 'description']
            data_list = list(models.BankAccount.objects.values(
                *data_cols_args).filter(**filter_params).order_by(ordering)[limit_start:limit_end])

            # 데이터 복호화 수행
            for data in data_list:
                data['account'] = get_dec_value(data.get('account'))
                data['description'] = get_dec_value(data.get('description'))

            # 전체 레코드 수 조회
            records_total = models.BankAccount.objects.filter(**filter_params).count()

            return JsonResponse(
                {'draw': draw, 'recordsTotal': records_total, 'recordsFiltered': records_total, 'data': data_list})

        except Exception as e:
            logger.warning(f'[BankAccountAPI - get] {to_str(e)}')
            return HttpResponse(status=400)

    @method_decorator(permission_required('note.add_bankaccount', raise_exception=True))
    def post(self, request):
        # 감사 로그 > 내용
        actions = []

        # 감사 로그 > 결과
        result = False
        try:
            bank = get_dic_value(request.POST, 'bank')
            account = get_dic_value(request.POST, 'account')
            account_holder = get_dic_value(request.POST, 'account_holder')
            description = get_dic_value(request.POST, 'description')

            # 데이터 암호화 수행
            enc_account = make_enc_value(account)
            enc_description = make_enc_value(description)

            # DB에 데이터 추가
            data = models.BankAccount(
                bank=bank,
                account=enc_account,
                account_holder=account_holder,
                description=enc_description,
            )
            data.save()

            # 추가 성공 시 감사 로그 > 내용에 아이디 항목 추가
            actions.append(f'[아이디] : {to_str(data.id)}')

            result = True
            return HttpResponse(status=201)

        except Exception as e:
            logger.warning(f'[BankAccountAPI - post] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            # 감사 로그 기록
            actions.append(f'[은행] : {bank}')
            actions.append(f'[예금주] : {account_holder}')
            audit_log = f"""추가 ( {', '.join(actions)} )"""

            insert_audit_log(request.user.id, request, category, '-', audit_log, result)

    @method_decorator(permission_required('note.change_bankaccount', raise_exception=True))
    def put(self, request, req_id):
        # 감사 로그 > 내용
        actions = []
        actions.append(f'[아이디] : {to_str(req_id)}')

        # 감사 로그 > 결과
        result = False
        try:
            if req_id:

                # put data 파싱
                put_data = MultiPartParser(request.META, request, request.upload_handlers).parse()[0]

                bank = get_dic_value(put_data, 'bank')
                account = get_dic_value(put_data, 'account')
                account_holder = get_dic_value(put_data, 'account_holder')
                description = get_dic_value(put_data, 'description')

                # id 기준으로 항목 조회
                data = models.BankAccount.objects.get(pk=to_int(req_id))

                # 변경 사항이 존재하는 항목 수정
                if data.bank != bank:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[은행] : {to_str(data.bank)} → {bank}')

                    # 항목 수정
                    data.bank = bank

                enc_account = make_enc_value(account)
                if data.account != enc_account:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[계좌번호 변경]')

                    # 항목 수정
                    data.account = enc_account

                if data.account_holder != account_holder:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[예금주] : {to_str(data.account_holder)} → {account_holder}')

                    # 항목 수정
                    data.account_holder = account_holder

                enc_description = make_enc_value(description)
                if data.description != description:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[설명 변경]')

                    # 항목 수정
                    data.description = enc_description

                # 변경 사항 적용
                data.save()
                result = True

                return HttpResponse(status=204)

        except Exception as e:
            logger.warning(f'[BankAccountAPI - put] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            # 감사 로그 기록
            audit_log = f"""편집 ( {', '.join(actions)} )"""
            insert_audit_log(request.user.id, request, category, '-', audit_log, result)

    @method_decorator(permission_required('note.delete_bankaccount', raise_exception=True))
    def delete(self, request, req_id):
        # 감사 로그 > 내용
        actions = []
        actions.append(f'[아이디] : {to_str(req_id)}')

        # 감사 로그 > 결과
        result = False

        try:
            if req_id:
                # 삭제할 항목 조회
                data = models.BankAccount.objects.get(pk=req_id)

                bank = to_str(data.bank)
                account_holder = to_str(data.account_holder)

                # 삭제 수행
                data.delete()
                result = True

                return HttpResponse(status=204)

        except Exception as e:
            logger.warning(f'[BankAccountAPI - delete] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            # 감사 로그 기록
            actions.append(f'[은행] : {bank}')
            actions.append(f'[예금주] : {account_holder}')
            audit_log = f"""삭제 ( {', '.join(actions)} )"""

            insert_audit_log(request.user.id, request, category, '-', audit_log, result)

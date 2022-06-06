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
category = '시리얼 번호 관리'


# 시리얼 번호 관리
class SerialView(TemplateView):
    template_name = 'note/serial.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class SerialAPI(View):
    @method_decorator(permission_required('note.view_serial', raise_exception=True))
    def get(self, request):
        try:
            # 컬럼 리스트
            column_list = ('type', 'title', 'value', 'description')

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

                    # 유형
                    if filter_name == 'type':
                        insert_dic_data(filter_params, 'type', value)

                    # 제품 명
                    elif filter_name == 'title':
                        insert_dic_data(filter_params, 'title__icontains', value)

                    # 시리얼 번호
                    elif filter_name == 'value':
                        insert_dic_data(filter_params, 'value__icontains', value)

                    # 설명
                    elif filter_name == 'description':
                        insert_dic_data(filter_params, 'description__icontains', value)

            data_cols_args = ['id', 'type', 'title', 'value', 'description']
            data_list = list(models.Serial.objects.values(
                *data_cols_args).filter(**filter_params).order_by(ordering)[limit_start:limit_end])

            # 데이터 복호화 수행
            for data in data_list:
                data['value'] = get_dec_value(data.get('value'))
                data['description'] = get_dec_value(data.get('description'))

            # 전체 레코드 수 조회
            records_total = models.Serial.objects.filter(**filter_params).count()

            return JsonResponse(
                {'draw': draw, 'recordsTotal': records_total, 'recordsFiltered': records_total, 'data': data_list})

        except Exception as e:
            logger.warning(f'[SerialAPI - get] {to_str(e)}')
            return HttpResponse(status=400)

    @method_decorator(permission_required('note.add_serial', raise_exception=True))
    def post(self, request):
        # 감사 로그 > 내용
        actions = []

        # 감사 로그 > 결과
        result = False
        try:
            serial_type = get_dic_value(request.POST, 'type')
            title = get_dic_value(request.POST, 'title')
            value = get_dic_value(request.POST, 'value')
            description = get_dic_value(request.POST, 'description')

            # 데이터 암호화 수행
            enc_value = make_enc_value(value)
            enc_description = make_enc_value(description)

            # DB에 데이터 추가
            data = models.Serial(
                type=serial_type,
                title=title,
                value=enc_value,
                description=enc_description,
            )
            data.save()

            # 추가 성공 시 감사 로그 > 내용에 아이디 항목 추가
            actions.append(f'[아이디] : {to_str(data.id)}')

            result = True
            return HttpResponse(status=201)

        except Exception as e:
            logger.warning(f'[SerialAPI - post] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            # 감사 로그 기록
            actions.append(f'[유형] : {serial_type}')
            actions.append(f'[제품 명] : {title}')
            audit_log = f"""추가 ( {', '.join(actions)} )"""

            insert_audit_log(request.user.id, request, category, '-', audit_log, result)

    @method_decorator(permission_required('note.change_serial', raise_exception=True))
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

                serial_type = get_dic_value(put_data, 'type')
                title = get_dic_value(put_data, 'title')
                value = get_dic_value(put_data, 'value')
                description = get_dic_value(put_data, 'description')

                # id 기준으로 항목 조회
                data = models.Serial.objects.get(pk=to_int(req_id))

                # 변경 사항이 존재하는 항목 수정
                if data.type != serial_type:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[유형] : {to_str(data.type)} → {serial_type}')

                    # 항목 수정
                    data.type = serial_type

                if data.title != title:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[제품 명] : {to_str(data.title)} → {title}')

                    # 항목 수정
                    data.title = title

                enc_value = make_enc_value(value)
                if data.value != enc_value:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[시리얼 번호 변경]')

                    # 항목 수정
                    data.value = enc_value

                enc_description = make_enc_value(description)
                if data.description != enc_description:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[설명 변경]')

                    # 항목 수정
                    data.description = enc_description

                # 변경 사항 적용
                data.save()
                result = True

                return HttpResponse(status=204)

        except Exception as e:
            logger.warning(f'[SerialAPI - put] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            # 감사 로그 기록
            audit_log = f"""편집 ( {', '.join(actions)} )"""
            insert_audit_log(request.user.id, request, category, '-', audit_log, result)

    @method_decorator(permission_required('note.delete_serial', raise_exception=True))
    def delete(self, request, req_id):
        # 감사 로그 > 내용
        actions = []
        actions.append(f'[아이디] : {to_str(req_id)}')

        # 감사 로그 > 결과
        result = False

        try:
            if req_id:
                # 삭제할 항목 조회
                data = models.Serial.objects.get(pk=req_id)

                serial_type = to_str(data.type)
                title = to_str(data.title)

                # 삭제 수행
                data.delete()
                result = True

                return HttpResponse(status=204)

        except Exception as e:
            logger.warning(f'[SerialAPI - delete] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            # 감사 로그 기록
            actions.append(f'[유형] : {serial_type}')
            actions.append(f'[제품 명] : {title}')
            audit_log = f"""삭제 ( {', '.join(actions)} )"""

            insert_audit_log(request.user.id, request, category, '-', audit_log, result)


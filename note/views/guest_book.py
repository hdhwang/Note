from django.http import HttpResponse, JsonResponse
from django.http.multipartparser import MultiPartParser
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.views.generic import TemplateView, View
from note import models
from note.util.dicHelper import insert_dic_data, get_dic_value
from note.util.formatHelper import *
from note.util.logHelper import insert_audit_log
from note.util.regexHelper import *

import logging
logger = logging.getLogger(__name__)

# 감사 로그 > 카테고리
category = '결혼식 방명록'


# 결혼식 방명록
class GuestBookView(TemplateView):
    template_name = 'note/guest_book.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class GuestBookAPI(View):
    @method_decorator(permission_required('note.view_guestbook', raise_exception=True))
    def get(self, request):
        try:
            # 컬럼 리스트
            column_list = ('name', 'amount', 'date', 'area', 'attend', 'description')

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

                    # 이름
                    if filter_name == 'name':
                        insert_dic_data(filter_params, 'name__icontains', value)

                    # 금액
                    elif filter_name == 'amount':
                        insert_dic_data(filter_params, 'amount', value)

                    # 장소
                    elif filter_name == 'area':
                        insert_dic_data(filter_params, 'area__icontains', value)

                    # 참석 여부
                    elif filter_name == 'attend':
                        insert_dic_data(filter_params, 'attend', value)

                    # 설명
                    elif filter_name == 'description':
                        insert_dic_data(filter_params, 'description__icontains', value)

            data_cols_args = ['id', 'name', 'amount', 'date', 'area', 'attend', 'description']
            val = list(models.GuestBook.objects.values(
                *data_cols_args).filter(**filter_params).order_by(ordering)[limit_start:limit_end])

            # 전체 레코드 수 조회
            records_total = models.GuestBook.objects.filter(**filter_params).count()

            return JsonResponse(
                {'draw': draw, 'recordsTotal': records_total, 'recordsFiltered': records_total, 'data': val})

        except Exception as e:
            logger.warning(f'[GuestBookAPI - get] {to_str(e)}')
            return HttpResponse(status=400)

    @method_decorator(permission_required('note.add_guestbook', raise_exception=True))
    def post(self, request):
        # 감사 로그 > 내용
        actions = []

        # 감사 로그 > 결과
        result = False
        try:
            name = get_dic_value(request.POST, 'name')
            amount = to_int(get_dic_value(request.POST, 'amount', None))
            date = get_dic_value(request.POST, 'date', None)
            area = get_dic_value(request.POST, 'area')
            attend = get_dic_value(request.POST, 'attend', '-')
            description = get_dic_value(request.POST, 'description')

            # DB에 데이터 추가
            data = models.GuestBook(
                name=name,
                amount=amount,
                date=date,
                area=area,
                attend=attend,
                description=description,
            )
            data.save()

            # 추가 성공 시 감사 로그 > 내용에 아이디 항목 추가
            actions.append(f'[아이디] : {to_str(data.id)}')

            result = True
            return HttpResponse(status=201)

        except Exception as e:
            logger.warning(f'[GuestBookAPI - post] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            date_str = date if date is not None else ''
            amount_str = to_str(amount) if amount is not None else ''

            # 감사 로그 기록
            actions.append(f'[이름] : {name}')
            actions.append(f'[금액] : {amount_str}')
            actions.append(f'[일자] : {date_str}')
            actions.append(f'[장소] : {area}')
            actions.append(f'[참석 여부] : {self.get_attend_str(attend)}')
            actions.append(f'[설명] : {description}')
            audit_log = f"""추가 ( {', '.join(actions)} )"""

            insert_audit_log(request.user.id, request, category, '-', audit_log, result)

    @method_decorator(permission_required('note.change_guestbook', raise_exception=True))
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

                name = get_dic_value(put_data, 'name')
                amount = to_int(get_dic_value(put_data, 'amount', None))
                date = get_dic_value(put_data, 'date', None)
                area = get_dic_value(put_data, 'area')
                attend = get_dic_value(put_data, 'attend', '-')
                description = get_dic_value(put_data, 'description')

                # id 기준으로 항목 조회
                data = models.GuestBook.objects.get(pk=to_int(req_id))

                # 변경 사항이 존재하는 항목 수정
                if data.name != name:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[이름] : {to_str(data.name)} → {name}')

                    # 항목 수정
                    data.name = name

                if data.amount != amount:
                    org_amount_str = to_str(data.amount) if data.amount else ''
                    amount_str = to_str(amount) if amount is not None else ''

                    # 감사 로그 > 내용 추가
                    actions.append(f'[금액] : {org_amount_str} → {amount_str}')

                    # 항목 수정
                    data.amount = amount

                org_date_str = datetime_to_str(data.date, '%Y-%m-%d') if data.date else ''
                date_str = date if date is not None else ''
                if org_date_str != date_str:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[일자] : {org_date_str} → {date_str}')

                    # 항목 수정
                    data.date = date

                if data.area != area:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[장소] : {to_str(data.area)} → {area}')

                    # 항목 수정
                    data.area = area

                if data.attend != attend:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[참석 여부] : {self.get_attend_str(data.attend)} → {self.get_attend_str(attend)}')

                    # 항목 수정
                    data.attend = attend

                if data.description != description:
                    # 감사 로그 > 내용 추가
                    actions.append(f'[설명] : {to_str(data.description)} → {description}')

                    # 항목 수정
                    data.description = description

                # 변경 사항 적용
                data.save()
                result = True

                return HttpResponse(status=204)

        except Exception as e:
            logger.warning(f'[GuestBookAPI - put] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            # 감사 로그 기록
            audit_log = f"""편집 ( {', '.join(actions)} )"""
            insert_audit_log(request.user.id, request, category, '-', audit_log, result)

    @method_decorator(permission_required('note.delete_guestbook', raise_exception=True))
    def delete(self, request, req_id):
        # 감사 로그 > 내용
        actions = []
        actions.append(f'[아이디] : {to_str(req_id)}')

        # 감사 로그 > 결과
        result = False

        try:
            if req_id:
                # 삭제할 항목 조회
                data = models.GuestBook.objects.get(pk=req_id)

                name = data.name
                amount = to_str(data.amount) if data.amount else ''
                date = datetime_to_str(data.date, '%Y-%m-%d') if data.date else ''
                area = data.area
                attend = self.get_attend_str(data.attend)
                description = data.description

                # 삭제 수행
                data.delete()
                result = True

                return HttpResponse(status=204)

        except Exception as e:
            logger.warning(f'[GuestBookAPI - delete] {to_str(e)}')
            return HttpResponse(status=400)

        finally:
            # 감사 로그 기록
            actions.append(f'[이름] : {name}')
            actions.append(f'[금액] : {amount}')
            actions.append(f'[일자] : {date}')
            actions.append(f'[장소] : {area}')
            actions.append(f'[참석 여부] : {attend}')
            actions.append(f'[설명] : {description}')
            audit_log = f"""삭제 ( {', '.join(actions)} )"""

            insert_audit_log(request.user.id, request, category, '-', audit_log, result)

    def get_attend_str(self, data):
        result = ''
        if data == 'Y':
            result = '참석'

        elif data == 'N':
            result = '미참석'

        elif data == '-':
            result = '미정'

        return result

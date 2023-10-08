from django.shortcuts import HttpResponseRedirect, render
from django.http import JsonResponse, HttpResponse
from django.http.multipartparser import MultiPartParser
from django.conf import settings
from django.views.generic import TemplateView, View
from note.jwt.tokens import verify_token, get_token

import json
import logging
import math
import re
import requests

logger = logging.getLogger(__name__)
table_filter_regex = re.compile("filter\[[0-9]{1,3}\]\[value\]")

class IndexView(TemplateView):
    template_name = "note/index.html"
    context = {}

    def get(self, request):
        access_token = request.COOKIES.get('access')
        if access_token:
            # 유효한 토큰이 존재하는 경우 대시보드로 이동
            verify_response = verify_token(access_token)
            if verify_response.status_code == 200:
                return HttpResponseRedirect("/dashboard")
        return self.render_to_response(self.context)


# 로그인
class LoginView(View):
    def post(self, request):
        try:
            token_response = get_token(request)
            response = HttpResponse(status=token_response.status_code)
            if token_response.status_code == 200 and token_response.json():
                response.set_cookie('access', token_response.json().get('access'))
                response.set_cookie('refresh', token_response.json().get('refresh'))
                response.set_cookie('access_exp', token_response.json().get('access_exp'))
                response.set_cookie('refresh_exp', token_response.json().get('refresh_exp'))
            return response

        except Exception as e:
            logger.warning(f"[LoginView - post] {str(e)}")
            return HttpResponse(status=400)

# 로그아웃
class LogoutView(View):
    def get(self, request):
        try:
            response = HttpResponseRedirect("/")
            response.delete_cookie('access')
            response.delete_cookie('refresh')
            response.delete_cookie('access_exp')
            response.delete_cookie('refresh_exp')
            return response

        except Exception as e:
            logger.warning(f"[LogoutView - get] {str(e)}")
            return HttpResponse(status=400)


# HTTP 상태 코드 400
def error_400(request, exception):
    response = render(request, "note/error/400.html")
    response.status_code = 400
    return response


# HTTP 상태 코드 401
def error_401(request, message=""):
    response = render(request, "note/error/401.html", {"message": message})
    return response


# HTTP 상태 코드 403
def error_403(request, exception):
    response = render(request, "note/error/403.html")
    response.status_code = 403
    return response


# HTTP 상태 코드 404
def error_404(request, exception):
    response = render(request, "note/error/404.html")
    response.status_code = 404
    return response


# HTTP 상태 코드 500
def error_500(request):
    response = render(request, "note/error/500.html")
    response.status_code = 500
    return response


class DataTablesKoreanView(View):
    def get(self, request):
        s_length_menu = request.GET.get("s-length-menu", "페이지당 줄수")
        response = {
            "sEmptyTable": "데이터가 없습니다.",
            "sInfo": "_START_ - _END_ / _TOTAL_",
            "sInfoEmpty": "0 - 0 / 0",
            "sInfoFiltered": "(총 _MAX_ 개)",
            "sInfoPostFix": "",
            "sInfoThousands": ",",
            "sLengthMenu": f"{s_length_menu} _MENU_",
            "sLoadingRecords": "조회중...",
            "sProcessing": "처리중...",
            "sSearch": "검색:",
            "sZeroRecords": "검색 결과가 없습니다.",
            "oPaginate": {
                "sFirst": "처음",
                "sLast": "마지막",
                "sNext": "다음",
                "sPrevious": "이전",
            },
            "oAria": {"sSortAscending": ": 오름차순 정렬", "sSortDescending": ": 내림차순 정렬"},
        }
        return JsonResponse(response)


class TableAPIView(View):
    base_url = getattr(settings, "API_BASE_URL")
    sub_path = ""

    def get(self, request, *args, **kwargs):
        try:
            params = {}
            page = 1
            page_size = 10
            start = 0

            # LIMIT 및 필터 설정
            for param in request.GET.items():
                key = param[0]
                value = param[1]

                if key == "start":
                    start = int(value) + 1

                elif key == "length" and int(value) > 0:
                    page_size = int(value)

                # XSS 방지를 위한 파라미터
                elif key == "draw":
                    draw = value

                # 정렬 설정
                elif key == "order[order]":
                    req_ordering = value
                    req_order_dir = request.GET.get("order[dir]")
                    params["ordering"] = req_order_dir + req_ordering

                # 필터 설정
                elif table_filter_regex.search(key) and value != "":
                    filter_key = f'{key.split("[value]")[0]}[data]'
                    filter_name = request.GET.get(filter_key)
                    params[filter_name] = value

            if start > 0:
                page = math.ceil(start / page_size)

            params["page"] = page
            params["page_size"] = page_size
            headers = {
                "Authorization": f"Bearer {kwargs.get('access_token')}",
                "Content-Type": "application/json",
            }
            response = requests.get(
                f"{self.base_url}/{self.sub_path}",
                params=params,
                headers=headers,
                verify=False,
            )
            if response.status_code == 200 and response.json():
                data = response.json().get("results")
                count = response.json().get("count")
                return JsonResponse(
                    {
                        "draw": draw,
                        "recordsTotal": count,
                        "recordsFiltered": count,
                        "data": data,
                    }
                )
            return HttpResponse(status=response.status_code)
        except Exception as e:
            logger.warning(f"[TableAPIView - get] {str(e)}")
            return HttpResponse(status=400)

    def post(self, request, *args, **kwargs):
        try:
            data = {}
            for key, value in request.POST.items():
                data[key] = value
            headers = {
                "Authorization": f"Bearer {kwargs.get('access_token')}",
                "Content-Type": "application/json",
            }
            response = requests.post(
                f"{self.base_url}/{self.sub_path}",
                data=json.dumps(data),
                headers=headers,
                verify=False,
            )
            return HttpResponse(status=response.status_code)

        except Exception as e:
            logger.warning(f"[TableAPIView - post] {str(e)}")
            return HttpResponse(status=400)

    def put(self, request, req_id, *args, **kwargs):
        try:
            if req_id:
                # put data 파싱
                put_data = MultiPartParser(
                    request.META, request, request.upload_handlers
                ).parse()[0]
                data = {}
                for key, value in put_data.items():
                    data[key] = value
                headers = {
                    "Authorization": f"Bearer {kwargs.get('access_token')}",
                    "Content-Type": "application/json",
                }
                response = requests.put(
                    f"{self.base_url}/{self.sub_path}/{req_id}",
                    data=json.dumps(data),
                    headers=headers,
                    verify=False,
                )
                return HttpResponse(status=response.status_code)

        except Exception as e:
            logger.warning(f"[TableAPIView - put] {str(e)}")
            return HttpResponse(status=400)

    def delete(self, request, req_id, *args, **kwargs):
        try:
            if req_id:
                headers = {
                    "Authorization": f"Bearer {kwargs.get('access_token')}",
                    "Content-Type": "application/json",
                }
                response = requests.delete(
                    f"{self.base_url}/{self.sub_path}/{req_id}",
                    headers=headers,
                    verify=False,
                )
                return HttpResponse(status=response.status_code)

        except Exception as e:
            logger.warning(f"[TableAPIView - delete] {str(e)}")
            return HttpResponse(status=400)

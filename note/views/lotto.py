from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
from note.util.formatHelper import *

import random
import requests

import logging
logger = logging.getLogger(__name__)


class LottoView(TemplateView):
    template_name = 'note/lotto.html'
    context = {}

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.context)


class LottoAPI(View):
    def get(self, request):
        draw = ''
        total = 5

        try:
            # LIMIT 및 필터 설정
            for param in request.GET.items():
                key = param[0]
                value = param[1]

                # XSS 방지를 위한 파라미터
                if key == 'draw':
                    draw = value

            val = self.gen_lotto_by_statistics()

            return JsonResponse({'draw': draw, 'recordsTotal': total, 'recordsFiltered': total, 'data': val})

        except Exception as e:
            logger.warning(f'[LottoAPI - get] {to_str(e)}')
            return HttpResponse(status=400)

    def gen_lotto_by_statistics(self):
        result = []

        try:
            base_url = 'https://dhlottery.co.kr/gameResult.do?method=statByNumber'
            con = requests.get(base_url)
            soup = BeautifulSoup(con.content, 'html.parser')
            stats_table = soup.find('table', {'class': 'tbl_data tbl_data_col'})

            stats_list = []
            ball_list = []

            for tr in stats_table.find_all('tr'):
                ball_data = []
                for td in tr.find_all('td'):
                    data = td.get_text()
                    if '\n\n' not in data:
                        ball_data.append(int(data))

                if ball_data:
                    stats_list.append(ball_data)

            for stats in stats_list:
                number = stats[0]
                count = stats[1]

                for i in range(count):
                    ball_list.append(number)

            random.shuffle(ball_list)

            for i in range(5):
                num_list = []
                str_num_list = ''

                for j in range(6):
                    lotto = random.choice(ball_list)
                    while lotto in num_list:
                        lotto = random.choice(ball_list)
                    num_list.append(lotto)

                num_list.sort()

                for j in range(6):
                    str_num = '%02d' % int(num_list[j])
                    str_num_list += str_num if str_num_list == '' else f', {str_num}'

                result.append({'num': chr(i+65), 'value': str_num_list})

        except Exception as e:
            logger.warning(f'[LottoAPI - gen_lotto_by_statistics] {to_str(e)}')
            return HttpResponse(status=400)

        return result

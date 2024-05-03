import datetime
import json

import requests
from django.core.mail import send_mail
from django.http import JsonResponse

from main.models import ChangeDiSub


TOKEN = '71d8a799496dff0b4a36dada2eacd6a6'


def get_wx_token(request):
    data = {'token': TOKEN}
    return JsonResponse(data)


# @csrf_exempt
def add_changdi_sub(request):
    # print(222222, )
    data = json.loads(request.body)
    sub_date = data.get('sub_date')
    sub_start_time = data.get('sub_start_time')
    sub_end_time = data.get('sub_end_time')
    sub_email = data.get('sub_email')

    sub_start_time = f'{sub_date} {sub_start_time}:00'
    sub_end_time = f'{sub_date} {sub_end_time}:00'

    ChangeDiSub.objects.create(
        sub_date=sub_date,
        sub_start_time=sub_start_time,
        sub_end_time=sub_end_time,
        sub_email=sub_email,
    )
    return JsonResponse({'success': True})


def req_papa(date_str):
    url = 'https://wx-api.papa.com.cn/v2'
    data = {
        'client_type': 'browser',
        'sport_tag_id': '1',
        'date_str': date_str,
        'r': 'stadia.skuList',
        'access_token_wx': TOKEN,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    resp = requests.post(url, data=data, headers=headers).json()
    # print(22222, json.dumps(resp, ensure_ascii=False))
    return resp


def parse(date_str):
    resp = req_papa(date_str)
    sku_list = resp['skuList']
    date_str = resp['date_str']
    data = [j for i in sku_list for j in i]
    return date_str, data


def split_time_by_30_minutes(start_time_str, end_time_str):
    start_time = datetime.datetime.strptime(start_time_str, '%H:%M')
    end_time = datetime.datetime.strptime(end_time_str, '%H:%M')
    interval = datetime.timedelta(minutes=30)
    current_time = start_time

    time_list = []
    while current_time <= end_time:
        time_list.append(current_time.strftime('%H:%M'))
        current_time += interval
        # print(current_time.strftime('%H:%M'))

    return time_list


def gene_half_an_hour_time_delta(time_list):
    delta_len = len(time_list)
    delta_list = []
    for i in range(delta_len - 1):
        delta_list.append(f'{time_list[i]}-{time_list[i+1]}')

    return delta_list


def get_has_changdi(changdi_sub, date_str, data):
    start_time = changdi_sub.sub_start_time.strftime('%H:%M')
    end_time = changdi_sub.sub_end_time.strftime('%H:%M')
    sub_date = changdi_sub.sub_date.strftime('%Y-%m-%d')

    time_list = split_time_by_30_minutes(start_time, end_time)
    # print(222222, start_time, end_time, sub_date, time_list)
    time_deltas = gene_half_an_hour_time_delta(time_list)
    # print(time_list, time_deltas)
    has_changdi = True
    if sub_date < date_str:
        return False
    for delta in time_deltas:
        if not [i for i in data if not i['is_lock'] and i['time_str'] == delta]:
            has_changdi = False
            break
    # print(has_changdi)
    return has_changdi


def monitor(request):
    cur_time = datetime.datetime.now()
    date_str = cur_time.strftime('%Y-%m-%d')
    # time_str = cur_time[-5:]
    # print(cur_time)
    res = ChangeDiSub.objects.filter(
        sub_date__gte=date_str,
        sub_start_time__gte=cur_time,
        sub_end_time__gte=cur_time,
        notified=False,
    )
    # print(res)

    for item in list(res):
        date_str, data = parse(item.sub_date.strftime('%Y-%m-%d'))
        has_changdi = get_has_changdi(item, date_str, data)
        print(item.sub_start_time, item.sub_end_time, has_changdi)
        if has_changdi:
            send_mail(
                '鹊山场地提醒',
                '',
                '690631890@qq.com',
                [i.strip() for i in item.sub_email.split(',') if i],
                html_message=f'您查询的{item.sub_date.strftime("%m月%d日")} {item.sub_start_time.strftime("%H:%M")}-{item.sub_end_time.strftime("%H:%M")}目前有空场，👉<a href="http://yuqiuquan.com">yuqiuquan.com</a>，速速订场哦～',
                fail_silently=False,
            )
            # break
            item.notified = True
            item.save(update_fields=['notified'])

    return JsonResponse({'success': True})

from django.http import JsonResponse


def get_wx_token(request):
    data = {'token': '71d8a799496dff0b4a36dada2eacd6a6'}
    return JsonResponse(data)

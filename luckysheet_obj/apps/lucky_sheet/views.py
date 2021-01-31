from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse, JsonResponse
from django.contrib import auth

import os
import json

base_dir = os.path.dirname(os.path.abspath(__file__))

from lucky_sheet import init_sheet
from lucky_sheet import websocket_server


# https://madewith.cn/709
# Create your views here.
def IndexView(request):
    return HttpResponse("success")


def luckysheet_update_url(request):
    websocket_server.websocket_update_url(request)


class LuckySheetIndex(View):
    def get(self, request):
        return render(request, "luckysheet.html", {})

    def post(self, request):
        return render(request, "luckysheet.html", {})


class LuckySheetLoadUrl(View):
    def get(self, request):
        print("get request")
        return HttpResponse({})

    def post(self, request):
        print("post request")
        init_json = init_sheet.init_sheet_json
        return HttpResponse('%s' % init_json)

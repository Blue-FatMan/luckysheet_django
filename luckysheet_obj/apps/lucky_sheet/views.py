from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse, JsonResponse
from django.contrib import auth
import os
import json
from lucky_sheet.log import logger

base_dir = os.path.dirname(os.path.abspath(__file__))

from lucky_sheet import init_sheet
from lucky_sheet import websocket_server


# https://madewith.cn/709
# Create your views here.
def IndexView(request):
    return HttpResponse("success")


def luckysheet_update_url(request):
    if request.method == "GET":
        return (websocket_server.websocket_update_url(request))
    elif request.method == "POST":
        return (websocket_server.websocket_update_image_url(request))
    else:
        return HttpResponse("error")


class LuckySheetIndex(View):
    def get(self, request):
        return render(request, "luckysheet.html", {})

    def post(self, request):
        return render(request, "luckysheet.html", {})


class LuckySheetLoadUrl(View):
    def get(self, request):
        logger.info("get request")
        return HttpResponse({})

    def post(self, request):
        logger.info("post request")
        init_json = init_sheet.init_sheet_json
        return HttpResponse('%s' % init_json)

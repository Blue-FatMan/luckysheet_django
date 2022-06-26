from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import auth
from django.conf import settings
import os
import json
import uuid

from lucky_sheet.log import logger
from lucky_sheet import init_sheet
from lucky_sheet import websocket_server
from lucky_sheet.tools import db

base_dir = os.path.dirname(os.path.abspath(__file__))
redis_obj = db.RedisDB(settings)


# https://madewith.cn/709
# Create your views here.

# index主页初始化
def IndexView(request):
    return render(request, "index.html", {})


# luckusheet的协同更新处理
def luckysheet_update_url(request):
    if request.method == "GET":
        return (websocket_server.websocket_update_url(request))
    elif request.method == "POST":
        return (websocket_server.websocket_update_image_url(request))
    else:
        return HttpResponse("error")


# demo主页
class LuckySheetIndex(View):
    def get(self, request):
        return render(request, "luckysheet.html", {"gridkey": ""})

    def post(self, request):
        return render(request, "luckysheet.html", {"gridkey": ""})


# 页面数据初始化加载
class LuckySheetLoadUrl(View):
    def get(self, request):
        logger.info("get request")
        return HttpResponse({})

    def post(self, request):
        logger.info("post request")
        gridkey = request.POST.get("gridKey", None)
        logger.info("gridkey: %s" % gridkey)
        init_json = init_sheet.init_sheet_json
        # 该判断是为了在用户刚开始上传excel的时候，点击保存数据库之后，从redis再加载一边数据，作为协同使用
        if gridkey:
            init_json = redis_obj.get_string(gridkey)
            if init_json != -1:
                init_json = json.loads(init_json)
                init_json = json.dumps(init_json.get("data"))
            else:
                init_json = dict()
        return HttpResponse('%s' % init_json)


# 保存数据库处理
class LuckySheetSaveDb(View):
    def get(self, request):
        return HttpResponse({})

    def post(self, request):
        #gridKey = str(uuid.uuid1())
        luckysheet_data = json.loads(request.POST.get("data"))
        gridKey = luckysheet_data.get('gridKey', str(uuid.uuid1()))
        luckysheet_data['allowUpdate'] = True
        luckysheet_data['updateUrl'] = settings.WSS_UPDATE_URL
        luckysheet_data['loadUrl'] = settings.WSS_LOAD_URL
        luckysheet_data['gridKey'] = gridKey
        redis_obj.insert_string(gridKey, '''%s''' % json.dumps(luckysheet_data))
        return HttpResponse(json.dumps({"status": 0, "data": luckysheet_data, "gridkey": gridKey}))


# 根据gridkey加载数据
class LuckySheetLoadGridKey(View):
    def get(self, request):
        gridKey = request.GET.get("gridKey")
        luckysheet_data = redis_obj.get_string(gridKey)
        if luckysheet_data:
            luckysheet_data = json.loads(luckysheet_data)
        else:
            logger.info("the gridkey does not exists %s" % gridKey)
            luckysheet_data = dict()
        return HttpResponse(json.dumps({"status": 0, "data": luckysheet_data, "gridkey": gridKey}))

    def post(self, request):
        return HttpResponse({})

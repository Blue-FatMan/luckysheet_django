#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@time: 2021/1/31 3:03
@author: LQ
@email: LQ65535@163.com
@File: websocket_server.py
@Software: PyCharm
"""

from django.shortcuts import render
from dwebsocket.decorators import accept_websocket, require_websocket
from django.http import HttpResponse
import json
from lucky_sheet import jvm_tool

WEB_SOCKET_CLIENT = list()


# https://blog.csdn.net/qq_36387683/article/details/99644041
@accept_websocket
def websocket_update_url(request):
    if not request.is_websocket():  # 判断是不是websocket连接
        return HttpResponse("the request is not a websocket request!!!")
    else:
        for message in request.websocket:
            if not message:
                message = "None"
            # 如果客户端长时间不活动，则会自动发送一个“rub”字符串到后台，因此做个过滤
            if "rub" in str(message):
                message = "None"
            if message != "None":
                jpy = jvm_tool.jpython_obj
                res = jpy.unCompressURI(message)
                res = json.loads(str(res))
                print("the web socket receive message message is: ", res)
                import time
                new_msg = {
                    "createTime": int(time.time() * 1000),
                    "data": "%s" % res,
                    "id": str(time.time()),
                    "returnMessage": "success",
                    "status": "0",
                    "type": 2,
                    "username": "LQ"
                }
                # return HttpResponse(json.dumps(new_msg), content_type='application/json')
                # request.websocket.send(bytes('{}'.format(new_msg), 'utf-8'))  # 发送消息到客户端
                request.websocket.send(json.dumps(new_msg))  # 发送消息到客户端

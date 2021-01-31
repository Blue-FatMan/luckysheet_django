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
import uuid
import time
from lucky_sheet import jvm_tool

WEB_SOCKET_CLIENT = dict()


# https://blog.csdn.net/qq_36387683/article/details/99644041
@accept_websocket
def websocket_update_url(request):
    userid = str(uuid.uuid1())
    # 每个客户端请求进来的时候，只会走一次这个流程，因此在这里面设置一个uuid
    if request.is_websocket():
        WEB_SOCKET_CLIENT[userid] = request.websocket
    if not request.is_websocket():  # 判断是不是websocket连接
        return HttpResponse("the request is not a websocket request!!!")
    else:
        for message in request.websocket:
            # 如果什么都没收到那就判定为客户端退出了
            if not message:
                print("the userid:%s has exit!!!" % userid)
                WEB_SOCKET_CLIENT[userid].close()
                del WEB_SOCKET_CLIENT[userid]
                return HttpResponse("the userid:%s has exit!!!" % userid)
            # 如果客户端长时间不活动，则会自动发送一个“rub”字符串到后台，因此做个过滤
            if "rub" in str(message):
                print(message)
                WEB_SOCKET_CLIENT[userid].send(message)
            else:
                jpy = jvm_tool.jpython_obj
                res = jpy.unCompressURI(message)
                res = json.loads(str(res))
                new_msg = {
                    "createTime": int(time.time() * 1000),
                    "data": "%s".replace("'", "\"") % res,
                    "id": "%s" % userid,
                    "returnMessage": "success",
                    "status": "0",
                    "type": 2,
                    "username": userid
                }
                # return HttpResponse(json.dumps(new_msg), content_type='application/json')
                # request.websocket.send(bytes('{}'.format(new_msg), 'utf-8'))  # 发送消息到客户端
                # request.websocket.send(json.dumps(new_msg))  # 发送消息到客户端
                for _client in WEB_SOCKET_CLIENT:
                    # 把自己的操作去掉，只给别的客户端更新操作
                    if _client != userid:
                        print("sed to %s" % _client)
                        request = WEB_SOCKET_CLIENT.get(_client)
                        print("the web socket receive message message is: ", new_msg)
                        # request.send(json.dumps(new_msg))  # 发送消息到客户端
                        request.send(json.dumps(new_msg))  # 发送消息到客户端
                        # request.send(bytes('{}'.format(new_msg), 'utf-8'))

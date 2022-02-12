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
from lucky_sheet.log import logger
from lucky_sheet import luckysheet_update
import urllib.parse
import zlib

WEB_SOCKET_CLIENT = dict()


# https://blog.csdn.net/qq_36387683/article/details/99644041


# 发送websocket消息
def send_websocket_message(userid, grid_key, res):
    luckysheet_update.update_operate(grid_key, res)
    # 添加多人协同编辑的时候，给其他人选区的位置标红
    # type: # 0：连接成功，1：发送给当前连接的用户，2：发送信息给其他用户，3：发送选区位置信息，999：用户连接断开
    t = res.get("t", None)
    if "mv" == t:
        __type = 3
    else:
        __type = 2
    new_msg = {
        "createTime": int(time.time() * 1000),
        "data": json.dumps(res),
        "id": "%s" % userid,
        "returnMessage": "success",
        "status": "0",
        "type": __type,
        "username": userid
    }
    for _client in list(WEB_SOCKET_CLIENT.keys()):
        # 把自己的操作去掉，只给别的客户端更新操作
        # 如果没有gridkey，则默认给所有没有gridkey的客户端同步消息，主要是首页演示使用
        if _client != userid:
            logger.info("sed to %s" % _client)
            request = WEB_SOCKET_CLIENT.get(_client).get("userid")
            # print("the web socket receive message message is: ", new_msg)
            request.send(json.dumps(new_msg))  # 发送消息到客户端

        # 如果有gridkey，则根据gridkey返回更新值，实际应用场景使用
        __gridkey = WEB_SOCKET_CLIENT.get(_client).get("grid_key", "")
        if not __gridkey:
            request = WEB_SOCKET_CLIENT.get(_client).get("userid")
            request.send(json.dumps(new_msg))  # 发送消息到客户端


@accept_websocket
def websocket_update_url(request):
    userid = str(uuid.uuid1())
    grid_key = request.GET.get("g", "")
    # 每个客户端请求进来的时候，只会走一次这个流程，因此在这里面设置一个uuid
    if request.is_websocket():
        WEB_SOCKET_CLIENT[userid] = dict()
        WEB_SOCKET_CLIENT[userid]["userid"] = request.websocket
        WEB_SOCKET_CLIENT[userid]["grid_key"] = grid_key
    if not request.is_websocket():  # 判断是不是websocket连接
        print("the request is not a websocket request!!!")
        return HttpResponse("the request is not a websocket request!!!")
    else:
        logger.info("txt message---")
        for message in request.websocket:
            # 如果什么都没收到那就判定为客户端退出了
            if not message:
                logger.info("the userid:%s has exit!!!" % userid)
                WEB_SOCKET_CLIENT[userid]["userid"].close()
                del WEB_SOCKET_CLIENT[userid]
                return HttpResponse("the userid:%s has exit!!!" % userid)
            # 如果客户端长时间不活动，则会自动发送一个“rub”字符串到后台，因此做个过滤
            if "rub" in str(message):
                res = {
                    "data": "rub",
                    "returnMessage": "success",
                }
                logger.info(message)
                WEB_SOCKET_CLIENT[userid]["userid"].send(json.dumps(res))
            else:
                # jpy = jvm_tool.jpython_obj
                # res = jpy.unCompressURI(message)
                destr = zlib.decompress(
                    bytes(message, 'ISO-8859-1'), zlib.MAX_WBITS | 16)
                result = urllib.parse.unquote_to_bytes(destr)
                res = json.loads(str(result, 'utf-8'))
                logger.info(res)
                send_websocket_message(userid, grid_key, res)


# 处理ajax接收到的图片消息
def websocket_update_image_url(request):
    grid_key = ""
    logger.info("images message---")
    res = json.loads(request.body)
    userid = res.get("username", "None")
    send_websocket_message(userid, grid_key, res)
    return HttpResponse("send images success!!!")

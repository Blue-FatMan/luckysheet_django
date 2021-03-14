#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@time: 2021/3/14 12:09
@author: LQ
@email: LQ65535@163.com
@File: redis.py
@Software: PyCharm
"""
# https://gitee.com/mengshukeji/LuckysheetServer/blob/main/luckysheet/src/main/java/com/xc/luckysheet/db/server/JfGridUpdateService.java
# import os
# import sys
# from pathlib import Path
# BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
# setting_path = os.path.join(BASE_DIR, "luckysheet_obj")
# sys.path.insert(0, setting_path)
# print(sys.path)
# from luckysheet_obj.luckysheet_obj import settings
# import redis
#
# redis_db = settings.MY_CACHES
# redis_host, redis_port = redis_db.get("LOCATION").split("//")[1].split(":")
# redis_max_connections = redis_db.get("OPTIONS", dict()).get("CONNECTION_POOL_KWARGS", dict()).get("max_connections")
#
#
# class RedisDB(object):
#     POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, max_connections=1000)
# _*_coding:utf-8_*_
import redis
import io
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luckysheet_obj.settings')


class RedisDB(object):
    def __init__(self, django_settings):
        self.pool = redis.ConnectionPool(host=django_settings.REDIS_CONN['HOST'],
                                         port=django_settings.REDIS_CONN['PORT'],
                                         db=django_settings.REDIS_CONN['DB'])
        self.redis = redis.Redis(connection_pool=self.pool)

    # string插入
    def insert_string(self, key, value):
        self.redis.set(key, value)

    # string取值
    def get_string(self, key):
        return self.redis.get(key)

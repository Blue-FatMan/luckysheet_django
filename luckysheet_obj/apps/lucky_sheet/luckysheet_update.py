#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@time: 2021/3/15 19:36
@author: LQ
@email: LQ65535@163.com
@File: luckysheet_update.py
@Software: PyCharm
"""
from django.conf import settings
import json
from lucky_sheet.tools import db

redis_obj = db.RedisDB(settings)


# 更新选择
def update_operate(grid_key, json_obj):
    t = json_obj.get("t")
    lucky_sheet = LuckySheetUpdate(grid_key, json_obj)
    if "sha" == t:
        # 插入新sheet页面
        lucky_sheet.insert_sheet()
    lucky_sheet.save_redis()


# LuckySheet后台更新类
class LuckySheetUpdate(object):
    def __init__(self, grid_key, json_obj):
        self.grid_key = grid_key
        self.json_obj = json_obj
        source_json_data = redis_obj.get_string(grid_key)
        if source_json_data:
            self.source_json_data = json.loads(source_json_data)
        else:
            self.source_json_data = {}

    # 插入新sheet页面
    def insert_sheet(self):
        """
        新增sheet页面的时候，需要找到data键,然后添加进去，data是一个列表形式，包含多个sheet页，可以直接append
        :return:
        """
        # TODO 待判断当前sheet是否在数据库中已经存在
        source_data = self.source_json_data.get("data", list())
        source_data.append(self.json_obj.get("v"))
        self.source_json_data["data"] = source_data

    # 保存到redis
    def save_redis(self):
        print(self.source_json_data)
        redis_obj.insert_string(self.grid_key, '''%s''' % json.dumps(self.source_json_data))

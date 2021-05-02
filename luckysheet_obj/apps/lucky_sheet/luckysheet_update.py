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
    # 插入新sheet页面
    if "sha" == t:
        lucky_sheet.insert_sheet()
    # 单个单元格刷新
    elif "v" == t:
        lucky_sheet.single_cell_refresh()
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
        source_data = self.source_json_data.get("data", list())
        new_sheet = self.json_obj.get("v")
        source_sheet_name = [_["name"] for _ in self.source_json_data["data"]]
        if new_sheet["name"] not in source_sheet_name:
            source_data.append(new_sheet)
        self.source_json_data["data"] = source_data

    # 单个单元格刷新
    def single_cell_refresh(self):
        """
        单元格更新的时候，celldata和data都要更新，celldata是记录二维数组的，data是直接的数据
        参考：https://mengshukeji.github.io/LuckysheetDocs/zh/guide/FAQ.html#dist%E6%96%87%E4%BB%B6%E5%A4%B9%E4%B8%8B%E4%B8%BA%E4%BB%80%E4%B9%88%E4%B8%8D%E8%83%BD%E7%9B%B4%E6%8E%A5%E8%BF%90%E8%A1%8C%E9%A1%B9%E7%9B%AE
        :return:
        """
        source_data = self.source_json_data.get("data", list())
        new_data = self.json_obj.get("v")
        new_i = self.json_obj.get("i")
        new_r = self.json_obj.get("r")
        new_c = self.json_obj.get("c")
        new_cell_data = dict()
        new_cell_data["r"] = new_r
        new_cell_data["c"] = new_c
        new_cell_data["v"] = new_data
        source_hasit = False
        for i, _ in enumerate(source_data):
            print("_[index], ", _["index"], type(_["index"]))
            if str(new_i) == str(_["index"]):
                for j, item in enumerate(_["celldata"]):
                    source_r, source_c = item["r"], item["c"]
                    if new_r == source_r and new_c == source_c:
                        self.source_json_data["data"][i]["celldata"][j]["v"].update(new_data)
                        source_hasit = True
                        break
                if not source_hasit:
                    self.source_json_data["data"][i]["celldata"].append(new_cell_data)
                self.source_json_data["data"][i]["data"][int(new_r)][int(new_c)] = new_data

    # 保存到redis
    def save_redis(self):
        print(self.source_json_data)
        redis_obj.insert_string(self.grid_key, '''%s''' % json.dumps(self.source_json_data))

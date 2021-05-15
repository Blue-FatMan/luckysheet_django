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
    # 范围单元格刷新
    elif "rv" == t:
        lucky_sheet.range_cell_refresh()
    # config操作
    elif "cg" == t:
        lucky_sheet.config_refresh()
    # 通用保存
    elif "all" == t:
        lucky_sheet.all_refresh()
    # 函数链操作
    elif "fc" == t:
        lucky_sheet.calc_chain_refresh()
    # 删除行或列
    elif "drc" == t:
        lucky_sheet.drc_refresh()

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
            self.source_json_data = {"data": []}
        self.source_data = self.source_json_data.get("data", list())

    # 插入新sheet页面
    def insert_sheet(self):
        """
        新增sheet页面的时候，需要找到data键,然后添加进去，data是一个列表形式，包含多个sheet页，可以直接append
        :return:
        """
        new_sheet = self.json_obj.get("v")
        source_sheet_name = [_["name"] for _ in self.source_json_data["data"]]
        if new_sheet["name"] not in source_sheet_name:
            null_array = self.null_array(new_sheet["row"], new_sheet["column"])
            new_sheet["data"] = null_array
            self.source_data.append(new_sheet)
        self.source_json_data["data"] = self.source_data

    # 单个单元格刷新
    def single_cell_refresh(self):
        """
        单元格更新的时候，celldata和data都要更新，celldata是记录二维数组的，data是直接的数据
        参考：https://mengshukeji.github.io/LuckysheetDocs/zh/guide/FAQ.html#dist%E6%96%87%E4%BB%B6%E5%A4%B9%E4%B8%8B%E4%B8%BA%E4%BB%80%E4%B9%88%E4%B8%8D%E8%83%BD%E7%9B%B4%E6%8E%A5%E8%BF%90%E8%A1%8C%E9%A1%B9%E7%9B%AE
        :return:
        """
        new_v = self.json_obj.get("v")
        new_i = self.json_obj.get("i")
        new_r = self.json_obj.get("r")
        new_c = self.json_obj.get("c")
        new_cell_data = dict()
        new_cell_data["r"] = new_r
        new_cell_data["c"] = new_c
        new_cell_data["v"] = new_v
        source_hasit = False
        for i, _ in enumerate(self.source_data):
            if str(new_i) == str(_["index"]):
                for j, item in enumerate(_["celldata"]):
                    source_r, source_c = item["r"], item["c"]
                    if new_r == source_r and new_c == source_c:
                        try:
                            if not self.source_json_data["data"][i]["celldata"][j].get("v", None):
                                self.source_json_data["data"][i]["celldata"][j]["v"] = {}
                            self.source_json_data["data"][i]["celldata"][j]["v"].update(new_v)
                        except:
                            # 如果更新过来的是直接的值，那么需要同时更新v和m，例如下面的
                            # {'t': 'v', 'i': 0, 'v': 8, 'r': 7, 'c': 0}
                            self.source_json_data["data"][i]["celldata"][j]["v"]["v"] = new_v
                            self.source_json_data["data"][i]["celldata"][j]["v"]["m"] = new_v
                        source_hasit = True
                        break
                if not source_hasit:
                    self.source_json_data["data"][i]["celldata"].append(new_cell_data)
                self.source_json_data["data"][i]["data"][int(new_r)][int(new_c)] = new_v

    # 范围单元格刷新
    def range_cell_refresh(self):
        """
        收到的数据如下, 范围单元格更新的时候，只会传过来左上角和右上角的坐标，需要自己对应一下
        {"t": "rv", "i": "1", "v": [[{"tb": 1, "v": "是的", "qp": 1, "m": "是的", "ct": {"fa": "@", "t": "s"}}, {}], [{}, {}], [{}, {"tb": 1, "v": "是", "qp": 1, "m": "是", "ct": {"fa": "@", "t": "s"}}]], "range": {"row": [10, 12], "column": [11, 12]}}
        :return:
        """
        new_v_list = self.json_obj.get("v")
        new_i = self.json_obj.get("i")
        left_upper = [self.json_obj.get("range")["row"][0], self.json_obj.get("range")["column"][0]]
        right_upper = [self.json_obj.get("range")["row"][1], self.json_obj.get("range")["column"][1]]

        new_r_i = 0  # 定义row的索引
        for new_r in range(left_upper[0], right_upper[0] + 1):
            new_c_i = 0  # 定义col的索引
            for new_c in range(left_upper[1], right_upper[1] + 1):
                new_v = new_v_list[new_r_i][new_c_i]
                # print(new_r, new_c, new_r_i, new_c_i, new_v)
                new_cell_data = dict()
                new_cell_data["r"] = new_r
                new_cell_data["c"] = new_c
                new_cell_data["v"] = new_v
                if not new_v:
                    new_v = {}
                source_hasit = False
                for i, _ in enumerate(self.source_data):
                    if str(new_i) == str(_["index"]):
                        for j, item in enumerate(_["celldata"]):
                            source_r, source_c = item["r"], item["c"]
                            if new_r == source_r and new_c == source_c:
                                self.source_json_data["data"][i]["celldata"][j]["v"].update(new_v)
                                source_hasit = True
                                break
                        if not source_hasit:
                            self.source_json_data["data"][i]["celldata"].append(new_cell_data)
                        self.source_json_data["data"][i]["data"][int(new_r)][int(new_c)] = new_v

                new_c_i = new_c_i + 1
            new_r_i = new_r_i + 1

    # config操作
    def config_refresh(self):
        """
        修改config中的某个配置时，会把这个配置全部传输到后台，即每次都把当前配置全部重新发送至后台
        :return:
        """
        new_v = self.json_obj.get("v")
        new_i = self.json_obj.get("i")
        new_k = self.json_obj.get("k")
        for i, _ in enumerate(self.source_data):
            if str(new_i) == str(_["index"]):
                self.source_json_data["data"][i]["config"].update({new_k: new_v})

    # 通用保存
    def all_refresh(self):
        new_v = self.json_obj.get("v")
        new_i = self.json_obj.get("i")
        new_k = self.json_obj.get("k")
        for i, _ in enumerate(self.source_data):
            if str(new_i) == str(_["index"]):
                self.source_json_data["data"][i].update({new_k: new_v})

    # 函数链操作
    def calc_chain_refresh(self):
        """
        函数链操作, 如果op的值为add则添加到末尾, update则更新pos索引，del则删除pos索引
        :return:
        """
        new_v = self.json_obj.get("v")
        try:
            new_v = json.loads(new_v)
        except:
            pass
        new_i = self.json_obj.get("i")
        new_op = self.json_obj.get("op")  # 操作类型,add为新增，update为更新，del为删除
        new_ops = self.json_obj.get("pos")  # 更新或者删除的函数位置
        for i, _ in enumerate(self.source_data):
            if str(new_i) == str(_["index"]):
                if not self.source_json_data["data"][i].get("calcChain", None):
                    self.source_json_data["data"][i]["calcChain"] = []
                if new_op == "add":
                    self.source_json_data["data"][i]["calcChain"].append(new_v)
                elif new_op == "update":
                    self.source_json_data["data"][i]["calcChain"][int(new_ops)].update(new_v)
                elif new_op == "del":
                    del self.source_json_data["data"][i]["calcChain"][int(new_ops)]
                else:
                    pass

    # 删除行或列
    def drc_refresh(self):
        """
        删除行或列, 如果rc的值是'r'删除行， 如果rc的值为'c'则删除列
        :return:
        """
        new_v = self.json_obj.get("v")
        new_v_index = int(new_v.get("index"))
        new_v_len = int(new_v.get("len"))
        new_i = self.json_obj.get("i")
        new_rc = self.json_obj.get("rc")
        for i, _ in enumerate(self.source_data):
            if str(new_i) == str(_["index"]):
                source_column = self.source_json_data["data"][i]["column"]
                source_row = self.source_json_data["data"][i]["row"]

                if new_rc == "r":
                    self.source_json_data["data"][i]["row"] = int(source_row) - new_v_len
                if new_rc == "c":
                    self.source_json_data["data"][i]["column"] = int(source_column) - new_v_len

                for j, item in enumerate(_["celldata"]):
                    source_r, source_c = item["r"], item["c"]
                    if new_rc == "r":
                        if new_v_index > int(source_r):
                            pass
                        elif new_v_index <= int(source_r) < new_v_index + new_v_len:
                            del self.source_json_data["data"][i]["celldata"][j]
                        else:
                            self.source_json_data["data"][i]["celldata"][j]["r"] = int(source_r) - new_v_len
                    if new_rc == "c":
                        if new_v_index > int(source_c):
                            pass
                        elif new_v_index <= int(source_c) < new_v_index + new_v_len:
                            del self.source_json_data["data"][i]["celldata"][j]
                        else:
                            self.source_json_data["data"][i]["celldata"][j]["c"] = int(source_c) - new_v_len

                if new_rc == "r":
                    for _ in range(new_v_len):
                        try:
                            del self.source_json_data["data"][i]["data"][new_v_index]
                        except:
                            pass

                    if new_rc == "c":
                        for data_i in range(len(self.source_json_data["data"][i]["data"])):
                            for _ in range(new_v_len):
                                try:
                                    del self.source_json_data["data"][i]["data"][data_i][new_v_index]
                                except:
                                    pass

    # 返回一个m行n列的一个空数组
    def null_array(self, m, n):
        """
        :param m:
        :param n:
        :return: 返回m行数组，每个数组有n列个空字典
        """
        m = int(m)
        n = int(n)
        array_data = []
        for i in range(m):
            tmp = []
            for j in range(n):
                tmp.append({})
            array_data.append(tmp)
        return array_data

    # 保存到redis
    def save_redis(self):
        # print(self.source_json_data)
        redis_obj.insert_string(self.grid_key, '''%s''' % json.dumps(self.source_json_data))

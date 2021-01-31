#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@time: 2021/1/31 2:56
@author: LQ
@email: LQ65535@163.com
@File: init_sheet.py
@Software: PyCharm
"""

# 初始化空excel的json
init_sheet_json = [
    {
        "name": "Cell",
        "index": "sheet_01",
        "order": 0,
        "status": 1,
        "celldata": [{"r": 0, "c": 0, "v": {"v": 1, "m": "1", "ct": {"fa": "General", "t": "n"}}}]
    },
    {
        "name": "Data",
        "index": "sheet_02",
        "order": 1,
        "status": 0
    },
    {
        "name": "Picture",
        "index": "sheet_03",
        "order": 2,
        "status": 0
    }
]

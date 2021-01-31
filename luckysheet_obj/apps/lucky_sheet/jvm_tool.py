#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@time: 2021/1/31 10:36
@author: LQ
@email: LQ65535@163.com
@File: jvm_tool.py
@Software: PyCharm
"""

import jpype
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

jarpath = os.path.join(base_dir, "java-utils.jar")  # 第二个参数是jar包的路径
jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % (jarpath))  # 启动jvm
JDClass = jpype.JClass("com.demo.utils.PakoGzipUtils")
jpython_obj = JDClass()  # 创建类的实例，可以调用类里边的方法

if __name__ == '__main__':
    jpype.shutdownJVM()  # 最后关闭jvm

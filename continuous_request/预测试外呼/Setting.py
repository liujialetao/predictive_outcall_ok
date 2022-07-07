#!/bin/python
import threading  # 导入threading模块

class Setting(object):

    def __init__(self,call_time=0):
        self.call_time = call_time
        self.status = True
        timer = threading.Timer(1, run)  # 每秒运行
        timer.start()  # 执行方法
        timer.

    def getCallTime(self):


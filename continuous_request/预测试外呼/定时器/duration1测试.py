import time
import datetime

class Duration():
    '''
    记录 开始、结束时间、持续时长 工作状态
    '''

    def __init__(self, start_time=None, duration=None, end_time=None):
        if end_time==None:
            # 开始时间
            self.start_time = start_time
            # 持续时长
            self.duration = datetime.timedelta(seconds=duration)
            # 结束时间
            self.end_time = self.start_time + self.duration
        elif duration==None:
            # 开始时间
            self.start_time = start_time
            # 结束时间
            self.end_time = end_time
            # 持续时长
            self.duration = self.end_time - self.start_time


now = datetime.datetime.now()
duration1 = Duration(now,5)
time.sleep(3)
now2 = datetime.datetime.now()
duration2 = Duration(start_time=now, duration=None, end_time=now2)

pass
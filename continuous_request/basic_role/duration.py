import datetime


class Duration():
    '''
    记录 开始、结束时间、持续时长
    '''

    def __init__(self, start_time=None, duration=None, end_time=None):
        if duration==None and end_time==None:
            self.start_time=start_time

        elif end_time==None:
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

        else:
            print('非法输入')


    def check_time_in_duration(self, check_time):
        '''
        判断检查时间点时，
        duration是未开始，进行中，已结束
        '''
        if check_time < self.start_time:
            return 'have_not_start'
        elif check_time >= self.start_time and check_time < self.end_time:
            return 'processing'
        else:
            return 'processed'
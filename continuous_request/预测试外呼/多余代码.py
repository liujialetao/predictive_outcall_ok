

class Predictors():

    def __init__(self, all_seats=4,
                 busy_seats=0,
                 busy_robots=0,
                 transfor_duration=30,
                 duration=40,
                 customer_tolerance_time=20,
                 ):
        '''
        参数：
        all_seats：人工坐席数
        busy_seats:忙碌的座席数
        ----------------------------------------
        busy_robots:机器人在呼数
        ----------------------------------------
        transfor_duration:转人工之前录音播放时长
        duration：人工坐席平均接听时长
        customer_tolerance_time:客户最大等待转人工时长
        ----------------------------------------

        '''
        #人工坐席参数
        self.all_seats = all_seats
        self.busy_seats = busy_seats
        self.idle_seats = self.all_seats - self.busy_seats

        #通话时长参数
        self.transfor_duration = transfor_duration
        self.duration = duration

        #客户等待的容忍度
        self.customer_tolerance_time = customer_tolerance_time

        #记录所有机器人的工作 每个元素是DurationRobot对象实例，记录机器人的开始工作时间、工作时长、结束工作时间
        self.robots_work_record = []
        #存放正在工作的机器人
        self.working_robots = []

        #记录所有人工坐席的工作
        self.seats_work_record = []


    def start_outbound(self):
        '''
        启动外呼服务
        '''
        # 更新参数
        self.update_params()

        #根据公式获取等待时间，在呼出
        waittime = self.judge_call_wait_time()
        time.sleep(waittime)
        #模拟接通率
        suc_call = np.random.choice(2,size=1,p=[0.7,0.3])




    def judge_call_wait_time(self, ):
        '''
        根据参数，决定呼叫间隔
        影响参数：

        ratio_transfer2manual

        '''
        pass


    def add_robot(self):
        '''

        '''
        pass


    def add_busy_seats(self):
        pass

    def update_params(self):
        '''
        更新参数
        '''
        self.busy_seats = self.busy_seats
        self.idle_seats = self.all_seats - self.busy_seats

        self.transfor_duration = self.transfor_duration
        self.duration = self.duration






    def get_busy_seats(self):
        '''

        '''

        #如果有接口获取参数

        pass






    def test_func(self):
        '''
        关注1： all_seats越小，稳定性越差，越容易出现呼损，越容易出现业务员等待时间过久
        关注2：
        '''
        pass
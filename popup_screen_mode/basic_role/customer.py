import datetime
import numpy as np
from .duration import Duration

class Customer():
    '''
    模拟客户行为
    状态1
        振铃时间段信息
    状态2
        是否接听电话
        与机器人聊天时间段
    状态3
        是否愿意转人工
        愿意等待转人工时间段
    状态4
        转人工是否成功
        人工坐席时间段
    状态5
        都结束了
    '''
    total_customer_num = 0
    def __init__(self, distribution_list, prob_list, ring_start_time:datetime.datetime, call_batch, random_seed):

        self.cal_customer_nums()
        if random_seed!=-1:
            #测试阶段，设置随机种子，利于复现
            np.random.seed(random_seed)

        average_ring_time, average_ring_time2, average_artificial_time = distribution_list
        prob_success_call, prob_transfer_to_artificial_seat = prob_list
        # 客户id
        self.customer_id = self.total_customer_num
        # 呼叫批次
        self.call_batch = call_batch

        #客户是否接电话  产生的概率为p
        self.answer_the_call = np.random.choice(['unsuccess_call','success_call' ],size=1,p=prob_success_call)[0]

        #如果接电话
        if self.answer_the_call == 'success_call':
            # 振铃 时间跨度记录
            f_ring_time = min(max(np.random.normal(loc=average_ring_time, scale=4), 0.01), 40)
            ring_time = f_ring_time
            self.ring_duration = Duration(start_time=ring_start_time,#振铃开始时间
                                                        duration=ring_time
                                                        )

            # 方法3
            self.need_artificial_seat = np.random.choice(['not_need_artificial_seat', 'need_artificial_seat'], size=1,
                                                         p=prob_transfer_to_artificial_seat)[0]
            if self.need_artificial_seat=='not_need_artificial_seat':

                not_need_duration = min(max(np.random.normal(loc=7, scale=4), 0), 120)

                self.robot_chat_duration = Duration(start_time=self.ring_duration.end_time,#机器人聊天开始时间
                                                            duration=not_need_duration
                                                            )


            elif self.need_artificial_seat == 'need_artificial_seat':

                minimum_duration_of_chat = 15

                self.robot_chat_duration = Duration(start_time=self.ring_duration.end_time,  # 机器人聊天开始时间
                                                    duration=minimum_duration_of_chat   #有意向的顾客，聊天时间肯定大于15秒
                                                    )
                f_robot_chat_duration = min(max(np.random.normal(loc=35.63, scale=6), minimum_duration_of_chat), 70)

                self.customer_tolerance_duration = Duration(start_time=self.robot_chat_duration.start_time+datetime.timedelta(seconds=minimum_duration_of_chat),
                                                            duration=f_robot_chat_duration-minimum_duration_of_chat
                                                           )

                # 模拟弹屏时间
                self.popup_screen_time = [self.customer_tolerance_duration.start_time]

                # 转人工成功与否 ‘unknow’   成功后，修改为'successful' 失败：'unsuccessful'
                self.success_transfer_to_artificial_seat = 'unknow'


        #如果不接电话 包括超过最大振铃时长无人接听
        elif self.answer_the_call == 'unsuccess_call':
            f_ring_time2 = min(max(np.random.normal(loc=average_ring_time2, scale=8), 0.01), 40)  # 40秒是振铃最大时长
            self.ring_duration = Duration(start_time=ring_start_time,
                                                        duration=f_ring_time2
                                                 )

        #每次检查时，记录customer的状态
        self.check_time_record = []


    @classmethod
    def init_total_customer_num(cls):
        cls.total_customer_num = 0

    @classmethod
    def cal_customer_nums(cls):
        cls.total_customer_num += 1


    def add_artificial_call(self, artifical_duration_start_time, average_artificial_time, debug=1):
        '''
        修改转人工坐席成功标记
        新增人工坐席时间段
        新增实际等待时间字段
        artifical_duration_start_time:转人工坐席的时间点
        '''
        # 修改转人工是否成功标记位

        self.success_transfer_to_artificial_seat = 'successful'

        f_artificial_duration = min(max(np.random.normal(loc=average_artificial_time, scale=10), 0.01), 300)  # 人工坐席最多服务300秒
        self.artificial_duration = Duration(start_time=artifical_duration_start_time, #转到人工坐席的开始时间
                                                        duration=f_artificial_duration
                                                        )


        if debug==1:
            # print('monitor_time   ', self.monitor_time_duration.start_time, self.monitor_time_duration.end_time)
            print('artificial_time', self.artificial_duration.start_time, self.artificial_duration.end_time)

    def print_customer_info(self):
        print('\t客户id:%d\t'%self.customer_id, '\t呼叫批次:%d\t'%self.call_batch, '振铃时间段：{}--{}'.format(self.ring_duration.start_time, self.ring_duration.end_time),end='\t')
        if self.answer_the_call=='unsuccess_call':
            print('呼叫失败')
        else:
            if self.need_artificial_seat=='need_artificial_seat':
                print('\n\t\t要人工坐席', '与AI聊天时间段：{}--{}'.format(self.robot_chat_duration.start_time, self.robot_chat_duration.end_time), '聊天时长{}秒'.format(self.robot_chat_duration.duration.total_seconds()))
                print('\t\t计划与AI聊天时间：{}--{}'.format(self.customer_tolerance_duration.start_time, self.customer_tolerance_duration.end_time))
                print('\t\t弹屏时间：{}'.format(self.robot_chat_duration.end_time))

            elif self.need_artificial_seat=='not_need_artificial_seat':
                print('不要人工坐席', '与AI聊天时间段：{}--{}'.format(self.robot_chat_duration.start_time, self.robot_chat_duration.end_time))

    @staticmethod
    def create_a_customer(distribution_list, pro_list, ring_start_time:datetime.datetime, call_batch, random_seed):
        '''
        模拟产生一个客户
        return Customer实例

        传入参数待扩充......
        '''
        new_customer = Customer(distribution_list, pro_list, ring_start_time, call_batch, random_seed)
        new_customer.print_customer_info()

        return new_customer


if __name__ == '__main__':
    print(123)

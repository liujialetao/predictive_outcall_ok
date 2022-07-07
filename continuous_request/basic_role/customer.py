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

        average_ring_time, average_ring_time2, average_artificial_time = distribution_list[0],distribution_list[1],distribution_list[2]
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
            f_ring_time = min(max(np.random.normal(loc=average_ring_time, scale=4), 0), 40)
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
                self.robot_chat_duration = Duration(start_time=self.ring_duration.end_time,  # 机器人聊天开始时间
                                                    duration=10
                                                    )
                f_robot_chat_duration = min(max(np.random.normal(loc=35.63, scale=6), 10), 70)

                # if f_robot_chat_duration>=10 and f_robot_chat_duration<=15:
                #     time_point_need_artificial_seat = 10
                # elif f_robot_chat_duration>15 and f_robot_chat_duration<=20:
                #     time_point_need_artificial_seat = np.random.choice([10,15], size=1, p=[0.6,0.4])[0]
                # elif f_robot_chat_duration>20:
                #     time_point_need_artificial_seat = np.random.choice([10,15,20],size=1, p=[0.4,0.3,0.3])[0]
                #
                # if f_robot_chat_duration-time_point_need_artificial_seat<=0:
                #     print('wait <0')
                self.customer_tolerance_duration = Duration(start_time=self.robot_chat_duration.start_time+datetime.timedelta(seconds=10),
                                                            duration=f_robot_chat_duration-10
                                                           )

                # 转人工成功与否 ‘unknow’   成功后，修改为'successful' 失败：'unsuccessful'
                self.success_transfer_to_artificial_seat = 'unknow'


        #如果不接电话 包括超过最大振铃时长无人接听
        elif self.answer_the_call == 'unsuccess_call':
            f_ring_time2 = min(max(np.random.normal(loc=average_ring_time2, scale=8), 0), 40)  # 40秒是振铃最大时长
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

    def get_customer_status(self, check_time:datetime.datetime):
        '''
        根据检查时的时间点  联合是否接电话，是否转人工
        判断客户处于什么状态，例如：
        状态1：振铃状态
        状态2：与机器人通话状态
        状态3：等待人工坐席状态  状态4：人工坐席状态
        状态5：结束状态  包括：振铃结束状态(不接电话的情况下)  机器人通话结束状态(不需要人工坐席的情况下)
        '''
        # self.check_time_sequence()
        # if self.customer_id==32 and check_time==datetime.datetime(2022,5,30,12,3,18):



        # 状态1判断 振铃状态
        if self.ring_duration.check_time_in_duration(check_time)=='processing':
            customer_status = 'ring_duration'
        elif self.ring_duration.check_time_in_duration(check_time)=='have_not_start':
            customer_status = 'not_start_ring_duration'
        # 如果不在振铃状态
        else:
            # 如果成功接听电话
            if self.answer_the_call=='success_call':
                # 状态2判断 与机器人通话状态
                if self.robot_chat_duration.check_time_in_duration(check_time)=='processing':
                    customer_status = 'robot_chat_duration'
                # 如果不在 与机器人通话状态
                else:
                    # 如果需要人工坐席
                    if self.need_artificial_seat=='need_artificial_seat':
                        #转人工成功与否未知
                        if self.success_transfer_to_artificial_seat=='unknow':
                            # 状态3判断 等待人工坐席
                            if self.customer_tolerance_duration.check_time_in_duration(check_time)=='processing':
                                customer_status = 'customer_tolerance_duration'
                            elif self.customer_tolerance_duration.check_time_in_duration(check_time)=='processed':
                                customer_status = 'call_loss'
                        elif self.success_transfer_to_artificial_seat=='successful':
                            if self.artificial_duration.check_time_in_duration(check_time)=='processing':
                                customer_status = 'artificial_seat_duration'
                            elif self.monitor_time_duration.check_time_in_duration(check_time)=='processing':
                                customer_status = 'monitor_time_duration'
                            else:
                                customer_status = 'over_artificial_seat_duration'
                        elif self.success_transfer_to_artificial_seat=='unsuccessful':
                            if hasattr(self, 'monitor_time_duration'):
                                if self.monitor_time_duration.check_time_in_duration(check_time)=='processing':
                                    customer_status = 'artificial_seat_duration'
                                elif self.monitor_time_duration.check_time_in_duration(check_time)=='processed':
                                    customer_status = 'over_monitor_time_duration'
                            else:
                                if self.customer_tolerance_duration.check_time_in_duration(check_time)=='processed':
                                    customer_status = 'call_loss'
                    # 如果不要人工座席
                    else:
                        if self.robot_chat_duration.check_time_in_duration(check_time)=='processed':
                            customer_status = 'over_robot_chat_duration'
            # 如果接电话失败
            else:
                # 如果不在振铃状态，任务结束----此判断可以省略
                if self.ring_duration.check_time_in_duration(check_time)=='processed':
                    customer_status = 'over_ring_duration'

        print('customer_id', self.customer_id, '检查时间点：', check_time, '客户状态：', customer_status)
        self.check_time_record.append((customer_status, check_time))

        return customer_status


    def add_artificial_call(self, artifical_duration_start_time, average_artificial_time, debug=1):
        '''
        修改转人工坐席成功标记
        新增人工坐席时间段
        新增实际等待时间字段
        artifical_duration_start_time:转人工坐席的时间点
        '''
        # 修改转人工是否成功标记位

        self.success_transfer_to_artificial_seat = 'successful'

        # 新增人工坐席时间段
        if self.customer_tolerance_duration.check_time_in_duration(artifical_duration_start_time)=='processing':
            f_artificial_duration = min(max(np.random.normal(loc=average_artificial_time, scale=10), 0.01), 300)  # 人工坐席最多服务300秒
            self.artificial_duration = Duration(start_time=artifical_duration_start_time, #转到人工坐席的开始时间
                                                            duration=f_artificial_duration
                                                            )
            if artifical_duration_start_time<self.customer_tolerance_duration.start_time:
                print('未开始')
            elif artifical_duration_start_time==self.customer_tolerance_duration.start_time:
                self.real_wait_duration = None
            else:
                self.real_wait_duration = Duration(start_time=self.customer_tolerance_duration.start_time, end_time=artifical_duration_start_time)
        else:
            print('逻辑有问题Customer add_artificial_call')


        if debug==1:
            print('monitor_time   ', self.monitor_time_duration.start_time, self.monitor_time_duration.end_time)
            print('artificial_time', self.artificial_duration.start_time, self.artificial_duration.end_time)

    def print_customer_info(self):
        print('\t客户id:%d\t'%self.customer_id, '\t呼叫批次:%d\t'%self.call_batch, '开始振铃：%s'%self.ring_duration.start_time, '结束振铃：%s'%self.ring_duration.end_time,end='\t')
        if self.answer_the_call=='success_call' and self.need_artificial_seat=='need_artificial_seat':
            print('需要人工坐席时间为:{}'.format(self.customer_tolerance_duration.start_time))
        else:
            print('不要人工坐席')

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

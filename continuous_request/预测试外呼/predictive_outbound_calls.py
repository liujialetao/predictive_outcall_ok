#!/bin/python
"""
坐席个数动态获取：
X1：接听中的客服
X2：空闲的客服

呼损：C0
呼叫接通率：C1
呼叫转人工率：C2

转人工之前与机器人通话时间：T0
人工通话时间：T1
机器人拨打电话的间隔时间：T2
客户等待容忍时间：T3

机器人总数量：N

F(X,T,C,N)得到YY   YY由T2控制
根据当前公式：
可以模拟出呼损
可以模拟每个客服的等待时间
"""

import numpy as np
import datetime
from typing import List

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
    def __init__(self, customer_id:int, ring_start_time:datetime.datetime, prob_success_call:List, prob_transfer_to_artificial_seat:List, random_seed):
        #测试阶段，设置随机种子，利于复现
        np.random.seed(random_seed)

        #客户id
        self.customer_id = customer_id

        #客户是否接电话  产生的概率为p
        self.answer_the_call = np.random.choice(['unsuccess_call','success_call' ],size=1,p=prob_success_call)[0]

        #如果接电话
        if self.answer_the_call == 'success_call':
            # 振铃 时间跨度记录
            # ring_time = min(max(np.random.normal(loc=5, scale=4),0), 40)#40秒是振铃最大时长
            ring_time = np.random.randint(low=1, high=8) #待调整
            self.ring_duration = Duration(start_time=ring_start_time,#振铃开始时间
                                                        duration=ring_time
                                                        )
            # 与机器人聊天 时间跨度记录
            self.robot_chat_duration = Duration(start_time=self.ring_duration.end_time,#机器人聊天开始时间
                                                        # duration=max(np.random.normal(loc=45, scale=30), 0)
                                                        duration=np.random.randint(low=15, high=20)  # 待调整
                                                        )
            # 愿意转人工的概率
            self.need_artificial_seat = np.random.choice(['not_need_artificial_seat', 'need_artificial_seat'], size=1, p=prob_transfer_to_artificial_seat)[0]
            if self.need_artificial_seat=='need_artificial_seat':
                # maximum_tolerance_time = max(np.random.normal(loc=30, scale=20), 1)
                maximum_tolerance_time = np.random.randint(low=15, high=20)  # 待调整

                # 客户等待转人工坐席 时间跨度记录
                self.customer_tolerance_duration = Duration(start_time=self.robot_chat_duration.end_time,
                                                        duration=maximum_tolerance_time
                                                        )
                #转人工成功与否 未知   成功后，修改为'successful' 失败：'unsuccessful'
                self.success_transfer_to_artificial_seat = 'unknow'

        #如果不接电话 包括超过最大振铃时长无人接听
        elif self.answer_the_call == 'unsuccess_call':
            # ring_time = min(max(np.random.normal(loc=5, scale=4),0), 40)#40秒是振铃最大时长
            ring_time = np.random.randint(low=1, high=8) #待调整
            self.ring_duration = Duration(start_time=ring_start_time,
                                                        duration=ring_time
                                                 )

        #每次检查时，记录customer的状态
        self.check_time_record = []

    def check_time_sequence(self):
        '''
        检查时间序列是不是有问题:
        检查1 振铃.start_time<=振铃.end_time
        检查2 振铃.end_time==与机器人聊天.start_time
        检查3 与机器人聊天.start_time<=与机器人聊天.end_time
        检查4 与机器人聊天.end_time==客户等待转人工坐席.start_time
        检查5
        '''
        try:
            if self.ring_duration.start_time<=self.ring_duration.end_time:
                pass
            else:
                print('检查1')

            if self.ring_duration.end_time==self.robot_chat_duration.start_time:
                pass
            else:
                print('检查2')

            if self.robot_chat_duration.start_time<=self.robot_chat_duration.end_time:
                pass
            else:
                print('检查3')

            if self.robot_chat_duration.end_time==self.customer_tolerance_duration.start_time:
                pass
            else:
                print('检查4')
        except:
            pass


    def get_customer_status(self, check_time:datetime.datetime):
        '''
        根据检查时的时间点  联合是否接电话，是否转人工
        判断客户处于什么状态，例如：
        状态1：振铃状态
        状态2：与机器人通话状态
        状态3：等待人工坐席状态
        状态4：结束状态  包括：振铃结束状态(不接电话的情况下)  机器人通话结束状态(不需要人工坐席的情况下)
        '''
        # self.check_time_sequence()
        def check_time_in_duration(duration, check_time):
            '''
            判断检查时间点时，
            duration是未开始，进行中，已结束
            '''
            if check_time < duration.start_time:
                return 'have_not_start'
            elif check_time>=duration.start_time and check_time<=duration.end_time:
                return 'processing'
            else:
                return 'processed'

        # 状态1判断 振铃状态
        if check_time_in_duration(self.ring_duration, check_time)=='processing':
            customer_status = 'ring_duration'
        elif check_time_in_duration(self.ring_duration, check_time)=='not_start':
            customer_status = 'not_start_ring_duration'
        # 如果不在振铃状态
        else:
            # 如果成功接听电话
            if self.answer_the_call=='success_call':
                # 状态2判断 与机器人通话状态
                if check_time_in_duration(self.robot_chat_duration, check_time)=='processing':
                    customer_status = 'robot_chat_duration'
                # 如果不在 与机器人通话状态
                else:
                    # 如果需要人工坐席
                    if self.need_artificial_seat=='need_artificial_seat':
                        #转人工成功与否未知
                        if self.success_transfer_to_artificial_seat=='unknow':
                            # 状态3判断 等待人工坐席
                            if check_time_in_duration(self.customer_tolerance_duration, check_time)=='processing':
                                customer_status = 'customer_tolerance_duration'
                            elif check_time_in_duration(self.customer_tolerance_duration, check_time)=='processed':
                                customer_status = 'call_loss'
                        elif self.success_transfer_to_artificial_seat=='successful':
                            if check_time_in_duration(self.artificial_duration, check_time)=='processing':
                                customer_status = 'artificial_seat_duration'
                            else:
                                customer_status = 'over_artificial_seat_duration'
                    # 如果不要人工座席
                    else:
                        if check_time_in_duration(self.robot_chat_duration, check_time)=='processed':
                            customer_status = 'over_robot_chat_duration'
            # 如果接电话失败
            else:
                # 如果不在振铃状态，任务结束----此判断可以省略
                if check_time_in_duration(self.ring_duration, check_time)=='processed':
                    customer_status = 'over_ring_duration'

        # 记录检查时间点
        if check_time == datetime.datetime(2022, 5, 30, 12, 0, 31) and self.customer_id==5:
            pass

        #     print('wati:', self.customer_id)
        # check_point = (customer_status, check_time)
        print('customer_id',self.customer_id, '检查时间点：',check_time, '客户状态：',customer_status)
        self.check_time_record.append((customer_status, check_time))
        return customer_status


    def add_artificial_call(self, check_time):
        # 如果愿意等带
        if self.transfer_to_artificial_seat==1:
            artificial_duration = min(max(np.random.normal(loc=50, scale=40),0), 300)#40秒是振铃最大时长
            self.artificial_duration = Duration(start_time=check_time, #转到人工坐席的开始时间
                                                            duration=artificial_duration
                                                            )
        else:
            print('出错，没有意愿转人工')



class OneOfArtificialSeat():
    '''
    模拟一个人工坐席
    坐席id
    已经处理的会话
    是否处于空闲状态
    '''
    def __init__(self, id, start_idle_time):
        # 坐席id
        self.id = id
        # 接线员已经处理的对话
        self.call_handled = []
        # 接线员工作状态  空闲为'idle' 忙碌为'busy'
        self.working_status = 'idle'
        # 接线员空闲时间段
        self.idle_duration = Duration(start_time=start_idle_time)

    def get_artificial_seat_status(self, check_time):
        '''
        查询坐席状态
        '''
        if self.working_status=='idle':
            return 'idle'
        elif self.working_status=='busy':
            # 根据当前时间，查询最后一个处理的cutomer
            last_customer = self.call_handled[-1]
            last_customer_status = last_customer.get_customer_status(check_time)

            # 如果人工坐席空闲 更新坐席工作状态
            if last_customer_status=='over_artificial_seat_duration':
                self.working_status = 'idle'


    def update_artificial_seat_status(self, check_time):
        '''
        根据检查时间点
        判断人工坐席是否忙线
        根据忙先状态，更新:
            工作状态
            空闲时间段
        '''
        # 如果坐席之前状态空闲，仅更新idle_duration
        if self.working_status=='idle':
             self.idle_duration = Duration(start_time=self.idle_duration.start_time,end_time=check_time)
        # 如果坐席之前状态忙碌
        elif self.working_status=='busy':
            # 根据当前时间，查询最后一个处理的cutomer
            last_customer = self.call_handled[-1]
            last_customer_status = last_customer.get_customer_status(check_time)

            # 如果人工坐席空闲，更新空闲开始时间，空闲时间段
            if last_customer_status=='over_artificial_seat_duration':
                self.working_status = 'idle'
                self.idle_duration = Duration(start_time=last_customer.artificial_duration.end_time,end_time=check_time)
            # 如果人工坐席忙碌  idle_duration置空
            else:
                self.idle_duration = None



    def add_call(self, customer):
        '''
        当人工坐席空闲时，加入一个客户
        '''
        if self.working_status=='busy':
            print('逻辑有问题')

        self.call_handled = self.call_handled.append(customer)


class ManageArtificialSeats():
    '''
    管理多个人工坐席
    '''
    def __init__(self, all_artificial_seats):
        self.all_artificial_seats = all_artificial_seats
        self.have_idle_seat = True


    def judge_idle_seat(self, check_time):
        '''
        判断是否有空闲坐席
        '''
        for artificial_seat in self.all_artificial_seats:
            if artificial_seat.get_artificial_seat_status(check_time)=='idle':
                self.have_idle_seat = True
                return True
        return False


    def get_idle_max_seat(self):
        '''
        在有空闲坐席的情况下
        找到空闲时间最久的人工坐席
        返回空闲的坐席
        '''

        start_idle_time = self.all_artificial_seats[0].idle_duration.start_time
        for artificial_seat in self.all_artificial_seats:
            if artificial_seat.call_handled == []:
                max_idle_seat = artificial_seat
                return max_idle_seat
            else:
                if start_idle_time < artificial_seat.idle_duration.start_time:
                    max_idle_seat = artificial_seat
        return  max_idle_seat



    def update_artificial_seats_status(self, the_most_urgent_customer, check_time):
        '''
        根据紧急的客户
        更新所有坐席状态
        '''
        # 如果有有空闲坐席
        if self.judge_idle_seat(check_time)==True:
            # 更新紧急客户的信息  成功转人工坐席
            the_most_urgent_customer.success_transfer_to_artificial_seat='successful'
            the_most_urgent_customer.real_tolerance_duration = None
            # duration = min(max(np.random.normal(loc=50, scale=40),0), 300)
            duration = np.random.randint(low=10, high=20)
            the_most_urgent_customer.artificial_duration = Duration(start_time=check_time, duration=duration)

            # 将客户交给坐席处理
            idle_max_seat = self.get_idle_max_seat()
            idle_max_seat.call_handled.append(the_most_urgent_customer)

            # # 更新人工坐席信息
            self.all_artificial_seats[idle_max_seat.id] = idle_max_seat

        else:
            print('等等看是否有空闲坐席')

        return the_most_urgent_customer




        print('123')


class ManageCustomers():
    '''
    管理正在工作的customer
    '''
    def __init__(self, customers_working=None):
        self.customers_working = customers_working

    def get_the_earliest_customer(self):
        '''
        在customers_working中，找到最早需要人工客服的customer
        '''

        the_most_urgent_customer = None

        for customer in self.customers_working:
            if hasattr(customer, 'need_artificial_seat'):
                if customer.need_artificial_seat=='need_artificial_seat':
                    if the_most_urgent_customer!=None:
                        if customer.robot_chat_duration.end_time < the_most_urgent_customer.robot_chat_duration.end_time:
                            the_most_urgent_customer = customer
                    elif the_most_urgent_customer==None:
                        the_most_urgent_customer = customer
        return the_most_urgent_customer



def get_the_latest_time(time_list):
    '''
    在所有时间点中，找到最晚的时间点
    '''
    the_latest_time_point = time_list[0]
    for time_point in time_list:
        if time_point > the_latest_time_point:
            the_latest_time_point = time_point
    return the_latest_time_point



def create_a_customer(customer_id:int, ring_start_time:datetime.datetime, prob_success_call:List, prob_transfer_to_artificial_seat:List, random_seed):
    '''
    模拟产生一个客户
    return Customer实例

    传入参数待扩充......
    '''
    customer = Customer(customer_id, ring_start_time, prob_success_call, prob_transfer_to_artificial_seat, random_seed)
    return customer


def update_customers_status(customers_working, customers_finished, customers_wait_transfer, customers_call_loss, check_time):
    '''
    根据当前检查时间，更新上个时间段在工作中的客户状态
    根据客户状态，将客户分类放入相应列表
    '''

    new_customers_working = []
    # 遍历customers_working中的customer状态
    for customer in customers_working:
        if customer.customer_id==7:
            print('2 wait')
        customer_status = customer.get_customer_status(check_time)
        # 如果customer在状态1 状态2 状态3， customer放在customers_working中
        if customer_status=='ring_duration' or customer_status=='robot_chat_duration' or customer_status=='customer_tolerance_duration':
            new_customers_working.append(customer)
        # 如果customer_status包含'over'字段， customer放在customers_finished中  并将
        elif 'over' in customer_status:
            customers_finished.append(customer)

        # 如果customer在状态1 状态2 状态3 状态4
        if customer_status=='customer_tolerance_duration':
            customers_wait_transfer.append(customer)

        if customer_status=='call_loss':
            customers_finished.append(customer)
            customers_call_loss.append(customer)

    return new_customers_working, customers_finished, customers_wait_transfer, customers_call_loss


#初始化参数，启动服务  初始化参数来自于前天数据或者经验值
prob_success_call = [0.2, 0.8] #客户 不接听、接听 的概率
prob_transfer_to_artificial_seat = [0.1,0.9] #客户 不愿意转人工、愿意转人工 的概率


customers_working = [] #正在工作中的customer
customers_finished = [] #结束任务的customer
customers_wait_transfer = [] #等待转人工坐席的customer
customers_call_loss = [] #转人工坐席失败的customer


now = datetime.datetime(2022,5,30,12,0,0)

N = 2 #人工坐席的个数
artificial_seats = [OneOfArtificialSeat(i, now) for i in range(N)]
mange_seats = ManageArtificialSeats(artificial_seats)
random_seed = np.arange(10000)

#初始化第一个客户id 创建客户的时间
customer_id = 1

# 根据当前时间产生第一个客户
new_customer = create_a_customer(customer_id, now, prob_success_call, prob_transfer_to_artificial_seat, random_seed[1])
customers_working.append(new_customer)

# 找到最紧急需要人工坐席的客服
manage_working_customers = ManageCustomers(customers_working)
the_most_urgent_customer = manage_working_customers.get_the_earliest_customer()
# 紧急客户需要人工坐席的时间点
if the_most_urgent_customer!=None:
    time_need_seat = the_most_urgent_customer.robot_chat_duration.end_time
else:
    time_need_seat=None

# 每隔T秒，计算一次发射时间
T = 5
period_calculate_time = now + datetime.timedelta(seconds=T)

# 计算wait_time时间
# wait_time = np.random.uniform(low=1, high=4)
wait_time = np.random.randint(low=1, high=4)#待调整
# 下次产生客户时间
next_time_create_customer = period_calculate_time + datetime.timedelta(seconds=wait_time)


while(True):

    # 如果对人工坐席没有需求  或者   下个客户产生时间<需要人工坐席时间
    if time_need_seat==None or (next_time_create_customer < time_need_seat):
        #产生一个客户
        customer_id += 1
        if customer_id == 7:
            print('wait id 7')
        new_customer = create_a_customer(customer_id, next_time_create_customer, prob_success_call, prob_transfer_to_artificial_seat, random_seed[customer_id])
        customers_working.append(new_customer)
        check_time = next_time_create_customer

    elif next_time_create_customer > time_need_seat:
        # 记录检查时间点
        check_time = time_need_seat
        # 用最紧急的客户，更新坐席管理
        mange_seats.update_artificial_seats_status(the_most_urgent_customer, check_time)

        pass

    print('customer_id   ', customer_id)
    if customer_id==7:
        print('wait id 7')
    # 更新客户状态
    customers_working, customers_finished, customers_wait_transfer, customers_call_loss = update_customers_status(customers_working, customers_finished, customers_wait_transfer, customers_call_loss, check_time)


    # 找到最紧急需要人工坐席的客服
    manage_working_customers = ManageCustomers(customers_working)
    the_most_urgent_customer = manage_working_customers.get_the_earliest_customer()
    # 紧急客户需要人工坐席的时间点
    if the_most_urgent_customer != None:
        time_need_seat = the_most_urgent_customer.robot_chat_duration.end_time
    else:
        time_need_seat = None


    # 计算wait_time时的时间
    period_calculate_time = period_calculate_time + datetime.timedelta(seconds=T)
    # 计算wait_time时间
    # wait_time = np.random.uniform(low=1, high=4)
    wait_time = np.random.randint(low=1, high=4)#待调整
    # 下个客户产生时间
    next_time_create_customer = period_calculate_time + datetime.timedelta(seconds=wait_time)













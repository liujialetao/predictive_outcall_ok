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
        状态3：等待人工坐席状态  状态4：人工坐席状态
        状态5：结束状态  包括：振铃结束状态(不接电话的情况下)  机器人通话结束状态(不需要人工坐席的情况下)
        '''
        # self.check_time_sequence()
        def check_time_in_duration(duration, check_time):
            '''
            判断检查时间点时，
            duration是未开始，进行中，已结束
            '''
            if check_time < duration.start_time:
                return 'have_not_start'
            elif check_time>=duration.start_time and check_time<duration.end_time:
                return 'processing'
            else:
                return 'processed'

        # 状态1判断 振铃状态
        if check_time_in_duration(self.ring_duration, check_time)=='processing':
            customer_status = 'ring_duration'
        elif check_time_in_duration(self.ring_duration, check_time)=='have_not_start':
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



        #     print('wati:', self.customer_id)
        # check_point = (customer_status, check_time)
        print('customer_id',self.customer_id, '检查时间点：',check_time, '客户状态：',customer_status)
        self.check_time_record.append((customer_status, check_time))
        return customer_status


    def add_artificial_call(self, artifical_duration_start_time):
        '''
        修改转人工坐席成功标记
        新增人工坐席时间段
        新增实际等待时间字段
        artifical_duration_start_time:转人工坐席的时间点
        '''
        # 修改转人工是否成功标记位
        self.success_transfer_to_artificial_seat = 'successful'
        if self.customer_id==22:
            print('ssss')
        # 新增人工坐席时间段
        if artifical_duration_start_time>= self.customer_tolerance_duration.start_time and artifical_duration_start_time<=self.customer_tolerance_duration.end_time:
            # artificial_duration = min(max(np.random.normal(loc=50, scale=40),0), 300)#40秒是振铃最大时长
            # np.random.seed(self.customer_id)
            artificial_duration = np.random.randint(low=15, high=20)#待调整
            self.artificial_duration = Duration(start_time=artifical_duration_start_time, #转到人工坐席的开始时间
                                                            duration=artificial_duration
                                                            )
            if artifical_duration_start_time==self.customer_tolerance_duration.start_time:
                self.real_wait_duration = None
            else:
                self.real_wait_duration = Duration(start_time=self.customer_tolerance_duration.start_time, end_time=artifical_duration_start_time)
        else:
            print('逻辑有问题Customer add_artificial_call')




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
                return 'idle'
            else:
                return 'busy'


    def add_a_customer(self, customer):
        '''
        给人工坐席，添加一个客户
        并修改坐席工作状态
        '''

        self.working_status = 'busy'

        self.call_handled.append(customer)

        self.idle_duration=None



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
            print('逻辑有问题add_call')

        self.call_handled = self.call_handled.append(customer)


class ManageArtificialSeats():
    '''
    管理多个人工坐席
    '''
    def __init__(self, all_artificial_seats):
        self.all_artificial_seats = all_artificial_seats
        self.have_idle_seat = True


    def update_have_idle_seat(self, check_time):
        '''
        判断是否有空闲坐席
        '''

        self.have_idle_seat = False
        # 如果有空闲坐席，更新
        for artificial_seat in self.all_artificial_seats:
            if artificial_seat.get_artificial_seat_status(check_time)=='idle':
                #只要有一个是空，退出循环
                self.have_idle_seat = True
                print('有空闲坐席')
                break

    def update_idle_seat_idle_time(self, check_time):
        '''
        在有空闲坐席的情况下
        更新每个坐席的idle_duration
        '''
        if self.have_idle_seat==False:
            print('逻辑有问题，在有空坐席的情况下，才能用')
        else:
            for artificial_seat in self.all_artificial_seats:
                if artificial_seat.get_artificial_seat_status(check_time)=='idle':
                    #如果之前状态已经是idle，不更新idle_duration
                    if artificial_seat.working_status == 'idle':
                        pass
                    #如果之间状态非空闲，当前的check_time作为空闲开始时间
                    else:
                        artificial_seat.working_status=='idle'
                        artificial_seat.idle_duration = Duration(start_time=check_time)

    def get_max_idle_seat(self, check_time):
        '''
        在有空闲坐席的情况下
        并且更新开始空闲时间
        '''
        if self.have_idle_seat==False:
            print('逻辑有问题get_max_idle_seat')

        else:
            # 如果有初始化过的坐席  一个客户还没接待
            for artificial_seat in self.all_artificial_seats:
                if artificial_seat.call_handled == []:
                    max_idle_seat = artificial_seat
                    return max_idle_seat

            # 否则，比较谁最先空闲
            real_idle_seats = []

            # 过滤掉忙碌的人工坐席  忙碌的人工座席，idle_duration是None
            for artificial_seat in self.all_artificial_seats:
                if artificial_seat.idle_duration!=None:
                    real_idle_seats.append(artificial_seat)

            max_idle_seat = real_idle_seats[0]
            start_idle_time = max_idle_seat.idle_duration.start_time

            for artificial_seat in real_idle_seats:
                if start_idle_time < artificial_seat.idle_duration.start_time :
                    max_idle_seat = artificial_seat

            return max_idle_seat

    def get_the_earliest_idle_seat(self):
        '''
        当坐席都在忙时
        找到最快获得空闲的坐席
        '''
        # 有空闲坐席时
        if self.have_idle_seat == True:
            for artificial_seat in self.all_artificial_seats:
                if artificial_seat.idle_duration!=None:
                    return  artificial_seat

        # 没有空闲坐席时，找到最早空闲的
        else:
            if customer_id==23:
                print('zhanzhu')
            the_earliest_idle_seat = self.all_artificial_seats[0]
            the_earliest_end_time = the_earliest_idle_seat.call_handled[-1].artificial_duration.end_time

            for artificial_seat in self.all_artificial_seats:
                last_customer = artificial_seat.call_handled[-1]
                end_time = last_customer.artificial_duration.end_time
                if end_time < the_earliest_end_time:
                    the_earliest_end_time = end_time
                    the_earliest_idle_seat = artificial_seat

            return the_earliest_idle_seat


class ManageCustomers():
    '''
    管理正在工作的customer
    '''
    def __init__(self, customers_working):
        self.customers_working = customers_working

    def get_the_earliest_customer(self):
        '''
        在customers_working中，找到最早需要人工客服的customer
        '''

        the_most_urgent_customer = None

        for customer in self.customers_working:
            # customer首先得阶段话，产生need_artificial_seat这个属性
            if hasattr(customer, 'need_artificial_seat'):
                #cutomer需要客服，并且没有接通过人工客服
                if customer.need_artificial_seat=='need_artificial_seat' and customer.success_transfer_to_artificial_seat=='unknow':
                    if the_most_urgent_customer!=None:
                        if customer.robot_chat_duration.end_time < the_most_urgent_customer.robot_chat_duration.end_time:
                            the_most_urgent_customer = customer
                    elif the_most_urgent_customer==None:
                        the_most_urgent_customer = customer
        return the_most_urgent_customer



def create_a_customer(customer_id:int, ring_start_time:datetime.datetime, prob_success_call:List, prob_transfer_to_artificial_seat:List, random_seed):
    '''
    模拟产生一个客户
    return Customer实例

    传入参数待扩充......
    '''
    print('create_a_customer   id:',customer_id)
    customer = Customer(customer_id, ring_start_time, prob_success_call, prob_transfer_to_artificial_seat, random_seed)
    return customer


def update_customers_status(customers_working, customers_finished, customers_wait_transfer, customers_call_loss, check_time):
    '''
    1
    根据当前检查时间，更新上个时间段在工作中的客户状态
    根据客户状态，将客户分类放入相应列表
    2
    根据当前时间，更新上个状态在等待转人工坐席的客户
    根据客户状态，将客户分类放入相应列表
    '''

    new_customers_working = []
    # 遍历customers_working中的customer状态
    for customer in customers_working:
        if customer.customer_id==2:
            print('2 wait')
        customer_status = customer.get_customer_status(check_time)
        # 如果customer在状态1 状态2 状态3， customer放在customers_working中
        if customer_status=='not_start_ring_duration' or customer_status=='ring_duration' or customer_status=='robot_chat_duration' or customer_status=='customer_tolerance_duration' or customer_status=='artificial_seat_duration':
            new_customers_working.append(customer)
        # 如果customer_status包含'over'字段， customer放在customers_finished中  并将
        elif 'over' in customer_status:
            customers_finished.append(customer)

        # 如果customer在状态1 状态2 状态3 状态4
        if customer_status=='customer_tolerance_duration':
            customers_wait_transfer.append(customer)

        if customer_status=='call_loss':
            customers_call_loss.append(customer)

    new_customers_working = list(set(new_customers_working))
    customers_wait_transfer = list(set(customers_wait_transfer))
    return new_customers_working, customers_finished, customers_wait_transfer, customers_call_loss


#初始化参数，启动服务  初始化参数来自于前天数据或者经验值
prob_success_call = [0.2, 0.8] #客户 不接听、接听 的概率
prob_transfer_to_artificial_seat = [0.1,0.9] #客户 不愿意转人工、愿意转人工 的概率


customers_working = [] #正在工作中的customer
customers_finished = [] #结束任务的customer
customers_wait_transfer = [] #等待转人工坐席的customer
customers_call_loss = [] #转人工坐席失败的customer

# 创建当前时间
now = datetime.datetime(2022,5,30,12,0,0)
# 下次拨号时间
next_time_create_customer = now

N = 2 #人工坐席的个数
# 创建N个人工坐席
artificial_seats = [OneOfArtificialSeat(i, now) for i in range(N)]
# 管理人工坐席
mange_seats = ManageArtificialSeats(artificial_seats)


#初始化第一个客户id 创建客户的时间
customer_id = 0
random_seed = np.arange(10000)
wait_time_seed = np.array([2,1,2,3,3,1,4,4,4,4]*100)
# 间隔T秒，检查一次拨号周期
T = 5

# 下次需要人工坐席的时间点，初始化为空
check_time = now

while(True):
    # 更新当前坐席的忙碌空闲状态
    mange_seats.update_have_idle_seat(check_time)
    print('此次检查的时间点：', check_time)

    # 管理正在工作的customer
    manage_working_customers = ManageCustomers(customers_working)
    # 找到最紧急需要人工坐席的客户
    the_most_urgent_customer = manage_working_customers.get_the_earliest_customer()

    # 判断当前坐席是否空闲
    if mange_seats.have_idle_seat==True:
        the_earliest_idle_seat = mange_seats.get_the_earliest_idle_seat()
        avalable_arificial_time = the_earliest_idle_seat.idle_duration.start_time
        # 更新坐席状态， 更新每个坐席的idle_duration
        mange_seats.update_idle_seat_idle_time(check_time)

        # 如果不要人工坐席
        if the_most_urgent_customer==None:
            customer_id += 1
            new_customer = create_a_customer(customer_id, next_time_create_customer, prob_success_call, prob_transfer_to_artificial_seat, random_seed[customer_id])
            customers_working.append(new_customer)
            check_time = next_time_create_customer
            print('check_time:没有坐席需求', check_time)

        # 如果有需要人工坐席的客户
        elif the_most_urgent_customer!=None:
            print('坐席有需求')

            # 获取需要人工坐席的时间点
            time_need_artificial = the_most_urgent_customer.robot_chat_duration.end_time
            # 如果需要人工坐席的时间点 大于 下次产生客户的时间点 （可能会产生time_need_artificial更小的cutomer）
            if time_need_artificial > next_time_create_customer:
                mode=1
                customer_id += 1
                new_customer = create_a_customer(customer_id, next_time_create_customer, prob_success_call, prob_transfer_to_artificial_seat, random_seed[customer_id])
                customers_working.append(new_customer)

                check_time = next_time_create_customer
                print('check_time:需求坐席时间，可能还会提前', check_time)
                artifical_duration_start_time = time_need_artificial

            # 客户转人工坐席
            else:
                if mode==1:
                    max_idle_seat = mange_seats.get_max_idle_seat(check_time)

                    # 如果转坐席时间，客户已经挂电话
                    # artifical_duration_start_time:人工坐席有空的时间点 或者 客户需要人工坐席的时间点
                    if artifical_duration_start_time > the_most_urgent_customer.customer_tolerance_duration.end_time:
                        customers_working, customers_finished, customers_wait_transfer, customers_call_loss = update_customers_status(
                            customers_working, customers_finished, customers_wait_transfer, customers_call_loss, check_time)

                    # elif artifical_duration_start_time ==

                    while (artifical_duration_start_time > the_most_urgent_customer.customer_tolerance_duration.end_time):
                        # 更新客户状态
                        check_time = artifical_duration_start_time
                        customers_working, customers_finished, customers_wait_transfer, customers_call_loss = update_customers_status( customers_working, customers_finished, customers_wait_transfer, customers_call_loss, check_time)

                        print('\n')
                    # 如果转作戏时间，还在和机器人聊天，不是在等待人工坐席


                    # 客户转到人工坐席
                    print('check_time:开始转转人工坐席', check_time, '紧急客户：',the_most_urgent_customer.customer_id )
                    the_most_urgent_customer.add_artificial_call(artifical_duration_start_time=artifical_duration_start_time)

                    # 将客户的aritificial_duration加入到坐席
                    max_idle_seat.add_a_customer(the_most_urgent_customer)

                elif mode==2:
                    max_idle_seat = mange_seats.get_max_idle_seat(check_time)

                    # 如果转坐席时间，客户已经挂电话
                    # artifical_duration_start_time:人工坐席有空的时间点 或者 客户需要人工坐席的时间点
                    if artifical_duration_start_time > the_most_urgent_customer.customer_tolerance_duration.end_time:
                        customers_working, customers_finished, customers_wait_transfer, customers_call_loss = update_customers_status(
                            customers_working, customers_finished, customers_wait_transfer, customers_call_loss,
                            check_time)

                    # elif artifical_duration_start_time ==

                    while (
                            artifical_duration_start_time > the_most_urgent_customer.customer_tolerance_duration.end_time):
                        # 更新客户状态
                        check_time = artifical_duration_start_time
                        customers_working, customers_finished, customers_wait_transfer, customers_call_loss = update_customers_status(
                            customers_working, customers_finished, customers_wait_transfer, customers_call_loss,
                            check_time)

                        print('\n')
                    # 如果转作戏时间，还在和机器人聊天，不是在等待人工坐席

                    # 客户转到人工坐席
                    print('check_time:开始转转人工坐席', check_time, '紧急客户：', the_most_urgent_customer.customer_id)
                    the_most_urgent_customer.add_artificial_call(
                        artifical_duration_start_time=artifical_duration_start_time)

                    # 将客户的aritificial_duration加入到坐席
                    max_idle_seat.add_a_customer(the_most_urgent_customer)



        # # 更新客户状态
        # customers_working, customers_finished, customers_wait_transfer, customers_call_loss = update_customers_status(
        #     customers_working, customers_finished, customers_wait_transfer, customers_call_loss, check_time)
        #
        # # 创建实例，找到最紧急需要人工坐席的客服
        # manage_working_customers = ManageCustomers(customers_working)

        # 周期性检查时间点
        t = now + datetime.timedelta(seconds=T * customer_id)
        # 获取等待时间
        wait_time = int(wait_time_seed[customer_id - 1])  # 待调整
        # 计算下次拨号时间
        next_time_create_customer = t + datetime.timedelta(seconds=wait_time)

    # 如果坐席不空   找到最先空闲的坐席，及其对应的时间点
    else:
        # mode2 找坐席开始空闲的时间
        mode = 2
        # 找到最早开始空闲坐席，及空闲开始时间点
        print('找不到空闲坐席')
        the_earliest_idle_seat = mange_seats.get_the_earliest_idle_seat()
        the_earliest_end_time = the_earliest_idle_seat.call_handled[-1].artificial_duration.end_time
        print('最快空闲的坐席时间：', the_earliest_end_time)
        if next_time_create_customer < the_earliest_end_time:
            customer_id += 1
            new_customer = create_a_customer(customer_id, next_time_create_customer, prob_success_call,
                                             prob_transfer_to_artificial_seat, random_seed[customer_id])
            if new_customer.customer_id==25:
                print('www')
            print('next_time_create_customer<the_earliest_end_time  customer_id:', new_customer.customer_id)
            customers_working.append(new_customer)

            check_time = next_time_create_customer # the_earliest_end_time<next_time_create_customer

            # 周期性检查时间点
            t = now + datetime.timedelta(seconds=T * customer_id)
            # 获取等待时间
            wait_time = int(wait_time_seed[customer_id - 1])  # 待调整
            # 计算下次拨号时间
            next_time_create_customer = t + datetime.timedelta(seconds=wait_time)


        check_time = the_earliest_end_time
        print('等待的空闲坐席，释放时间为：', the_earliest_end_time)
        print('下个客户产生时间为：', next_time_create_customer)


    # 根据当前时间，更新列表
    customers_working, customers_finished, customers_wait_transfer, customers_call_loss = update_customers_status(
        customers_working, customers_finished, customers_wait_transfer, customers_call_loss, check_time)


    print('此次检查结束\n\n')













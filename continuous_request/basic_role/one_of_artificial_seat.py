from .duration import Duration

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
            if last_customer.success_transfer_to_artificial_seat =='successful':
                last_customer_status = last_customer.get_customer_status(check_time)

                # 如果人工坐席空闲 更新坐席工作状态
                if last_customer_status=='over_artificial_seat_duration':
                    print('将要腾出的坐席由{}客户结束人工服务'.format(last_customer.customer_id))
                    return 'idle'
                else:
                    return 'busy'

            elif last_customer.success_transfer_to_artificial_seat =='unsuccessful':
                if last_customer.monitor_time_duration.check_time_in_duration(check_time)=='processed':
                    print('将要腾出的坐席由{}客户结束人工服务'.format(last_customer.customer_id))
                    return 'idle'
                else:
                    return 'busy'


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
            # 如果最后一个客户是成功转坐席的
            if last_customer.success_transfer_to_artificial_seat=='successful':
                last_customer_status = last_customer.get_customer_status(check_time)

                # 如果人工坐席空闲，更新空闲开始时间，空闲时间段
                if last_customer_status=='over_artificial_seat_duration':
                    self.working_status = 'idle'
                    self.idle_duration = Duration(start_time=last_customer.artificial_duration.end_time,end_time=check_time)
                # 如果人工坐席忙碌  idle_duration置空
                else:
                    self.idle_duration = None

            # 判断监听是否结束
            elif last_customer.success_transfer_to_artificial_seat=='unsuccessful':
                if self.monitor_time_duration.check_time_in_duration(check_time)=='processed':
                    self.idle_duration = Duration(start_time=last_customer.monitor_time_duration.end_time,
                                                  end_time=check_time)
                # 如果还在监听
                elif self.monitor_time_duration.check_time_in_duration(check_time)=='processing':
                    self.idle_duration = None

    def add_call(self, customer):
        '''
        当人工坐席空闲时，加入一个客户
        '''
        if self.working_status=='busy':
            print('逻辑有问题add_call')

        self.call_handled = self.call_handled.append(customer)


    def add_a_customer(self, customer):
        '''
        给人工坐席，添加一个客户
        并修改坐席工作状态
        '''
        if customer.success_transfer_to_artificial_seat == 'successful':

            self.working_status = 'busy'
            self.call_handled.append(customer)
            self.idle_duration=None

        elif customer.success_transfer_to_artificial_seat == 'unsuccessful':

            self.working_status = 'busy'
            self.call_handled.append(customer)
            self.idle_duration = None

    def find_avalable_arificial_time(self, initial_time, debug=1):

        # 如果一个客户还没接待
        if self.call_handled == []:
            avalable_arificial_time = initial_time
            # 记录由哪个客户释放
            the_earliest_end_customer_id = 0
        # 已经接待过客户的情况下
        else:
            last_customer = self.call_handled[-1]
            if last_customer.success_transfer_to_artificial_seat == 'successful':
                the_earliest_end_time = last_customer.artificial_duration.end_time
            elif last_customer.success_transfer_to_artificial_seat == 'unsuccessful':
                the_earliest_end_time = last_customer.monitor_time_duration.end_time
            avalable_arificial_time = the_earliest_end_time
            # 记录由哪个客户释放
            the_earliest_end_customer_id = last_customer.customer_id

        if debug==1:
            print('坐席空出的时间为：{}'.format(avalable_arificial_time),end='\t')
            if the_earliest_end_customer_id==0:
                print('坐席还没接待过客户')
            else:
                print('由客户id：{}空出'.format(the_earliest_end_customer_id))

        return avalable_arificial_time
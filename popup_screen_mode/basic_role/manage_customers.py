from .customer import Customer

class ManageCustomers():
    '''
    管理正在工作的customer
    '''

    def __init__(self, all_customers=[], occupy_seat_customers=[]):

        # 所有的客户
        self.all_customers = all_customers
        # 将可能要占用人工坐席的客户
        self.occupy_seat_customers = occupy_seat_customers

        #将类Customer的变量total_customer_num初始化为0
        self.init_class_customer()
        # print(self.all_customers,self.occupy_seat_customers)
        # print('123')

    def init_class_customer(self):

        Customer.init_total_customer_num()

    def update_occupy_seat_customers(self):
        '''
        根据客户的success_transfer_to_artificial_seat状态，更新occupy_seat_customers
            1 当 success_transfer_to_artificial_seat==‘successful’ 或者  success_transfer_to_artificial_seat==‘unsuccessful’
            说明已经处理过
            2 当 success_transfer_to_artificial_seat=='unknow'  说明需要坐席

        '''
        new_occupy_seat_customers = []
        for customer in self.occupy_seat_customers:
            if customer.success_transfer_to_artificial_seat == 'unknow':
                new_occupy_seat_customers.append(customer)
        self.occupy_seat_customers = new_occupy_seat_customers


    def get_the_earliest_popup_customer(self, debug=1):
        '''
        获取最早弹屏的客户  在success_transfer_to_artificial_seat=='unknow'的客户中寻找
        '''
        self.update_occupy_seat_customers()

        the_most_urgent_customer = None

        for customer in self.occupy_seat_customers:
            if the_most_urgent_customer!=None:
                if  customer.popup_screen_time[0] < the_most_urgent_customer.popup_screen_time[0]:
                    the_most_urgent_customer = customer
            elif the_most_urgent_customer==None:
                the_most_urgent_customer = customer

        if debug==1:
            if the_most_urgent_customer == None:
                print('没有客户需要坐席，开始拨号：')
            else:
                print( '紧急客户id：',the_most_urgent_customer.customer_id, '弹屏时间:', the_most_urgent_customer.popup_screen_time[0], '计划与AI聊天结束时间：',the_most_urgent_customer.customer_tolerance_duration.end_time)

        return the_most_urgent_customer


    def get_latest_batch_customers(self):
        '''
        获取最晚批次的客户
        '''

        get_the_latest_batch_id = self.all_customers[-1].call_batch
        all_customers = self.all_customers[::-1]

        latest_batch_customers = []
        for customer in all_customers:
            if customer.call_batch == get_the_latest_batch_id:
                latest_batch_customers.append(customer)
            else:
                break
        latest_batch_customers = latest_batch_customers[::-1]
        return latest_batch_customers


    @classmethod
    def get_latest_hang_up_time(cls, customers, debug=1):
        '''
        从customers，找到最晚挂机的客户
        '''
        def get_over_time(customer):
            '''
            返回没有意图客户的结束时间
            结束时间可能是
                1 振铃结束时间
                2 聊天结束时间
            '''
            if hasattr(customer, 'robot_chat_duration'):
                time_point = customer.robot_chat_duration.end_time
            else:
                time_point = customer.ring_duration.end_time
            return time_point


        target_costomer = customers[0]
        latest_time = get_over_time(target_costomer)
        for customer in customers[1:]:
            over_time = get_over_time(customer)
            if over_time > latest_time:
                target_costomer = customer
                latest_time = over_time


        if debug==1:
            print('呼叫批次：{}，没有坐席需求，最晚挂机或者聊天结束的客户id：{}，结束时间：{}'.format(target_costomer.call_batch, target_costomer.customer_id, latest_time))
        return target_costomer, latest_time


    @classmethod
    def get_latest_hang_up_time_mode3(cls, customers):
        '''
        cusotmer.need_artificial_seat=='need_artificial_seat'
        '''
        target_costomer = customers[0]
        latest_time = target_costomer.customer_tolerance_duration.end_time
        for customer in customers[1:]:
            over_time = customer.customer_tolerance_duration.end_time
            if over_time > latest_time:
                target_costomer = customer
                latest_time = over_time

        return target_costomer, latest_time


    @classmethod
    def get_latest_hang_up_time_mode2(cls, cusotmers):
        '''
        模式2：
            所有客户中，呼叫结束时间最晚的
            没有转接成功的客户
        '''

        # 分类 有意图转人工  没意图转人工(包括直接挂机的)
        intent_customers = []
        not_intent_customers = []
        for cusotmer in cusotmers:
            # 有意图的客户
            if hasattr(cusotmer, "need_artificial_seat") and cusotmer.need_artificial_seat=='need_artificial_seat':
                intent_customers.append(cusotmer)
            else:
                not_intent_customers.append(cusotmer)


        if not_intent_customers!=[]:
            latest_costomer1, latest_time1 = cls.get_latest_hang_up_time(not_intent_customers)

        if intent_customers!=[]:
            latest_costomer2, latest_time2 = cls.get_latest_hang_up_time_mode3(intent_customers)


        if not_intent_customers==[]:
            return latest_costomer2, latest_time2
        elif intent_customers==[]:
            return latest_costomer1, latest_time1
        else:
            if latest_time1 < latest_time2:
                return latest_costomer2, latest_time2
            else:
                return latest_costomer1, latest_time1



    def find_the_next_success_trans_to_seat_customer(self, avalable_arificial_time, debug=1):
        '''
        根据坐席可用时间avalable_arificial_time
        找到下个客户转进坐席的客户
        '''

        self.update_occupy_seat_customers()

        # 筛选可以转入的客户
        select_customers = []
        for customer in self.occupy_seat_customers:
            if customer.popup_screen_time[0] >= avalable_arificial_time:
                select_customers.append(customer)
            if customer.popup_screen_time[0] < avalable_arificial_time:
                customer.success_transfer_to_artificial_seat = 'unsuccessful'
                print('产生呼损的客户批次:{}， 客户id:{}'.format(customer.call_batch, customer.customer_id))

        if select_customers==[]:
            target_customer = None

        else:
            # 找到最早popup_screen的客户
            target_customer = select_customers[0]
            for customer in select_customers[1:]:
                if customer.popup_screen_time[0] < target_customer.popup_screen_time[0]:
                    target_customer = customer
                    # popup_screen_time = target_customer.popup_screen_time[0]
                    # target_customer_call_batch = target_customer.call_batch

        if debug==1:
            if target_customer==None:
                print('当前客户中，没有客户能够转进坐席')
            else:
                print('下次转进坐席的客户id:{}'.format(target_customer.customer_id), end='\t')
                print('弹屏时间:{}'.format(target_customer.popup_screen_time[0]))
        return target_customer





    def get_the_earliest_customer(self, debug=1):
        '''
        在working_customers中，找到最早需要人工客服的customer
        '''

        self.update_occupy_seat_customers()

        the_most_urgent_customer = None

        for customer in self.occupy_seat_customers:
            if the_most_urgent_customer!=None:
                if customer.popup_screen_time[0] < the_most_urgent_customer.popup_screen_time[0]:
                    the_most_urgent_customer = customer
            elif the_most_urgent_customer==None:
                the_most_urgent_customer = customer

        if debug==1:
            if the_most_urgent_customer==None:
                print('没有客户需要坐席，开始拨号：')
            else:
                print('需要坐席的客戶id：', end='\t')
                for customer in self.occupy_seat_customers:
                    print(customer.customer_id, end='\t')
                print('最早需要人工坐席的客户id： %s' % the_most_urgent_customer.customer_id, end='\t')
                print('弹屏时间：{}'.format(the_most_urgent_customer.popup_screen_time[0]))
        return the_most_urgent_customer


    @staticmethod
    def cal_C_I_D_ratio(working_customers):
        '''
        统计各种比例
        计算呼损

    A:人工通话平均时长
    C:电话接通率
    I:转人工比例 = 转人工数量/接通数量
    D：坐席接通失败率

    A = cal_busy_ration(manage_seats)
    C, I, D = cal_C_I_D_ratio(working_customers)
        '''
        # 统计成功拨通和未成功拨通的
        unsuccess_call_num = 0
        success_call_num = 0
        for customer in working_customers:
            if customer.answer_the_call == 'unsuccess_call':
                unsuccess_call_num += 1
            elif customer.answer_the_call == 'success_call':
                success_call_num += 1

        # 统计不需要人工坐席的
        not_need_artificial_seat_num = 0
        need_artificial_seat_num = 0
        success_transfer_to_artificial_seat = 0
        not_success_transfer_to_artificial_seat = 0
        unknow = 0
        for customer in working_customers:

            if customer.answer_the_call == 'success_call':
                if customer.need_artificial_seat == 'not_need_artificial_seat':
                    not_need_artificial_seat_num += 1

                elif customer.need_artificial_seat == 'need_artificial_seat':
                    need_artificial_seat_num += 1

                    if customer.success_transfer_to_artificial_seat == 'successful':
                        success_transfer_to_artificial_seat += 1
                    elif customer.success_transfer_to_artificial_seat == 'unsuccessful':
                        not_success_transfer_to_artificial_seat += 1

                    elif customer.success_transfer_to_artificial_seat == 'unknow':
                        unknow += 1
                else:
                    print('有问题')

        print('总共呼出:', unsuccess_call_num + success_call_num)
        print('未拨通的有:', unsuccess_call_num)
        print('拨通的有:', success_call_num)
        print()
        print('接通的情况下')
        print('不想要人工坐席的有:', not_need_artificial_seat_num)
        print('想要人工坐席的有:', need_artificial_seat_num)
        print('转人工坐席成功:', success_transfer_to_artificial_seat)
        print('转人工坐席不成功:', not_success_transfer_to_artificial_seat)
        print('还不知道结果:', unknow)
        print()
        success_call_ratio = success_call_num / (success_call_num + unsuccess_call_num)
        print('接通率为：{:.2f}%'.format((success_call_ratio * 100)))


        need_artificial_seat_ratio = need_artificial_seat_num / (
                    need_artificial_seat_num + not_need_artificial_seat_num)
        print('需要转坐席比例为:{:.2f}%'.format((need_artificial_seat_ratio * 100)))

        if (not_success_transfer_to_artificial_seat + success_transfer_to_artificial_seat)==0:
            print(123)
        call_loss_ration = not_success_transfer_to_artificial_seat / (
                not_success_transfer_to_artificial_seat + success_transfer_to_artificial_seat)
        print('呼损率:{:.2f}%'.format((call_loss_ration * 100)))
        print()

        I = success_transfer_to_artificial_seat / success_call_num
        print(' I:转人工比例 = 转人工数量/接通数量   I:{:.2f}%'.format(I*100))

        return success_call_ratio, I, call_loss_ration, need_artificial_seat_ratio
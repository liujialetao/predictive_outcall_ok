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
        print(self.all_customers,self.occupy_seat_customers)
        print('123')

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

    def get_the_earliest_customer(self, debug=1):
        '''
        在working_customers中，找到最早需要人工客服的customer
        '''

        self.update_occupy_seat_customers()

        the_most_urgent_customer = None

        for customer in self.occupy_seat_customers:
            if the_most_urgent_customer!=None:
                if customer.customer_tolerance_duration.start_time < the_most_urgent_customer.customer_tolerance_duration.start_time:
                    the_most_urgent_customer = customer
            elif the_most_urgent_customer==None:
                the_most_urgent_customer = customer

        if debug==1:
            if the_most_urgent_customer==None:
                print('没有客户需要坐席，开始拨号：')
            else:
                print('需要坐席的客戶有：', end='\t')
                for customer in self.occupy_seat_customers:
                    print(customer.customer_id, end='\t')
                print('最早需要人工坐席的客户id： %s' % the_most_urgent_customer.customer_id, end='\t')
                print('忍耐时间为：{}--{}'.format(the_most_urgent_customer.customer_tolerance_duration.start_time, the_most_urgent_customer.customer_tolerance_duration.end_time))
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
from .duration import Duration
import pandas as pd

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
                        artificial_seat.working_status='idle'
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

    def get_the_earliest_idle_seat(self, debug=1):
        '''
        当坐席都在忙时
        找到最快获得空闲的坐席
        '''
        # 有空闲坐席时
        if self.have_idle_seat == True:
            for artificial_seat in self.all_artificial_seats:
                # 如果idle_duration字段不为None 说明之前已经空闲
                if artificial_seat.idle_duration!=None:
                    the_earliest_idle_seat = artificial_seat

        # 没有空闲坐席时，找到最早空闲的
        else:
            the_earliest_idle_seat = self.all_artificial_seats[0]
            last_customer = the_earliest_idle_seat.call_handled[-1]

            if last_customer.success_transfer_to_artificial_seat=='successful':
                the_earliest_end_time = last_customer.artificial_duration.end_time
            elif last_customer.success_transfer_to_artificial_seat=='unsuccessful':
                the_earliest_end_time = last_customer.monitor_time_duration.end_time


            for artificial_seat in self.all_artificial_seats[1:]:
                last_customer = artificial_seat.call_handled[-1]
                # 获取人工坐席聊天结束时间
                if last_customer.success_transfer_to_artificial_seat == 'successful':
                    end_time = last_customer.artificial_duration.end_time
                elif last_customer.success_transfer_to_artificial_seat == 'unsuccessful':
                    end_time = last_customer.monitor_time_duration.end_time
                # 比较结束时间
                if end_time < the_earliest_end_time:
                    the_earliest_end_time = end_time
                    the_earliest_idle_seat = artificial_seat
        if debug==1:
            print('最先空出的坐席id为：{}'.format(the_earliest_idle_seat.id), end='\t')
        return the_earliest_idle_seat


    @staticmethod
    def cal_total_time(artificial_seat):
        '''
        计算单个坐席接第一个电话->挂最后一个电话的总时长
        '''
        first_customer = artificial_seat.call_handled[0]
        start_time = first_customer.ring_duration.start_time
        # if first_customer.success_transfer_to_artificial_seat == 'successful':
        #     start_time = first_customer.artificial_duration.start_time
        # else:
        #     start_time = first_customer.monitor_time_duration.start_time

        last_customer = artificial_seat.call_handled[-1]
        if last_customer.success_transfer_to_artificial_seat == 'successful':
            end_time = last_customer.artificial_duration.end_time
        else:
            end_time = last_customer.monitor_time_duration.end_time

        all_time = end_time - start_time
        days = all_time.days
        total_seconds = all_time.total_seconds()
        # 单个坐席接第一个电话->挂最后一个电话的总时长
        total_time = days * 24 * 3600 + total_seconds
        return total_time

    @staticmethod
    def cal_total_monitor_and_artificial_time(treated_customers, successful_flag):
        '''
        根据successful_flag，计算总时长
        args:
            successful_flag："successful" or "unsuccessful"
        '''
        count_num = 0
        # monitor_total_time = 0
        total_artificial_time = 0
        for customer in treated_customers:
            if customer.success_transfer_to_artificial_seat == successful_flag:
                count_num += 1
                # if customer.monitor_time_duration != None:
                #     monitor_total_time += customer.monitor_time_duration.duration.total_seconds()
                if hasattr(customer, "artificial_duration"):
                    total_artificial_time += customer.artificial_duration.duration.total_seconds()
        return count_num,  total_artificial_time

    @staticmethod
    def cal_busy_ration(manage_seats):
        '''
        1 检查1：多个坐席处理的客户是否有交集
        2 检查2：多个坐席处理的客户，客户时间上是否有交集
        3 统计坐席的忙占比
        4 return [{'successful':[接听数量, 监听总时长, 人工坐席总时长], 'unsuccessful':[监听数量, 监听总时长, 0] }] * 坐席个数
        '''

        def cal_average_parameter(row):
            '''
            计算均值
            df的列名：
Index(['total_time', 'successful_count_num',
       'successful_total_artificial_time'],
      dtype='object')
            '''
            # # 人工通话平均时长
            average_artificial_time_cal = row.successful_total_artificial_time / row.successful_count_num
            #
            # # 忙占比
            busy_ration = row.successful_total_artificial_time / row.total_time

            # 计算总共的空闲时间
            total_idle_time = row.total_time - row.successful_total_artificial_time

            # 计算平均空闲时长
            average_idle_time = total_idle_time / (row.successful_count_num - 1)

            if average_idle_time < 0:
                print('有错')
            if len(artificial_seat.call_handled) >= 2:
                print('\t总客户聊天时长为{:.0f}秒'.format(row.total_time))
                print('\t人工通话平均时长为{:.2f}秒'.format(average_artificial_time_cal))

                print('不考虑监听时长时：')
                print('\t忙占比为：{:.2f}%'.format(busy_ration * 100))
                print('\t进线时长为：{:.2f}秒'.format(average_idle_time))
            return average_artificial_time_cal, busy_ration, total_idle_time, average_idle_time


        if len(manage_seats.all_artificial_seats)!=1:
            # 检查1 两个坐席处理的客户是否有交集
            list_customer_id = []
            for artificial_seat in manage_seats.all_artificial_seats:

                for customer in artificial_seat.call_handled:
                    list_customer_id.append(customer.customer_id)

            if len(set(list_customer_id)) != len(list_customer_id):
                print('逻辑肯定有问题')

        # 检查2  每个坐席处理的客户，客户时间上是否有交集
        for artificial_seat in manage_seats.all_artificial_seats:
            artificial_duration_list = []

            for customer in artificial_seat.call_handled:
                if customer.success_transfer_to_artificial_seat == 'successful':
                    artificial_duration_list.append((customer.customer_id, customer.artificial_duration))
                else:
                    print('逻辑有问题 检查2  每个坐席处理的客户，客户时间上是否有交集')

            for i in range(len(artificial_duration_list) - 1):
                customer_id1, duration1 = artificial_duration_list[i]
                customer_id2, duration2 = artificial_duration_list[i + 1]

                if duration1.end_time > duration2.start_time:
                    print('逻辑肯定有问题')


        print('\n坐席的个数有{}个'.format(len(manage_seats.all_artificial_seats)))
        df = pd.DataFrame()
        for artificial_seat in manage_seats.all_artificial_seats:
            # 计算单个坐席接第一个电话->挂最后一个电话的总时长
            total_time = ManageArtificialSeats.cal_total_time(artificial_seat)
            # 统计成功转人工坐席，总数量，总监控时间，总人工坐席时间
            successful_count_num, successful_total_artificial_time = ManageArtificialSeats.cal_total_monitor_and_artificial_time(artificial_seat.call_handled, 'successful')


            dic = {
                "total_time":total_time,
                "successful_count_num":successful_count_num,
                "successful_total_artificial_time":successful_total_artificial_time,
            }

            df_new = pd.DataFrame([dic])
            df = df.append(df_new)
            print('坐席{}总时长为{:.0f}秒'.format(artificial_seat.id, total_time))
            average_artificial_time_cal, busy_ration, total_idle_time, average_idle_time= cal_average_parameter(df_new.iloc[0])

        return average_artificial_time_cal, busy_ration, total_idle_time, average_idle_time
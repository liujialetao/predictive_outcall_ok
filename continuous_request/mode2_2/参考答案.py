"""
模拟预测试外呼
1 计算拨号周期
2 呼叫模式1：间隔T=300秒，调整一次拨号间隔
"""
import datetime
import args
from args import prob_success_call, prob_transfer_to_artificial_seat, average_ring_time, average_ring_time2, average_artificial_time
import numpy as np
from continuous_request.public_configuration import now,next_time_create_customer
from continuous_request.basic_role import Duration, Customer, OneOfArtificialSeat, ManageArtificialSeats, ManageCustomers
from cal_wait_time import cal_wait_time, cal_flag, debug
from continuous_request.other_statistical_analysis import fitted_distribution

import pandas as pd
import os

def simulation(customer_num, next_time_create_customer, init_customer_wait_time, F, G):
    # 初始化第一个客户id 创建客户的时间
    customer_id = 0

    all_customers = []  # 所有的customer
    call_loss_customers = []  # 转人工坐席失败的customer
    success_trans = []  # 转人工坐席成功的customer
    # 创建N个人工坐席
    artificial_seats = [OneOfArtificialSeat(i, now) for i in range(args.H)]
    # 管理人工坐席
    manage_seats = ManageArtificialSeats(artificial_seats)
    # 管理正在工作的customer
    manage_customers = ManageCustomers(all_customers)

    # 下次需要人工坐席的时间点，初始化为空
    check_idle_time = now

    while(customer_id < customer_num):

        # 更新当前坐席的忙碌空闲状态
        manage_seats.update_have_idle_seat(check_idle_time)

        # 找到最紧急需要人工坐席的客户
        the_most_urgent_customer = manage_customers.get_the_earliest_customer()

        # 判断当前坐席是否空闲
        if manage_seats.have_idle_seat==True:
            # 找空闲醉酒的坐席，更新每个坐席的idle_duration
            manage_seats.update_idle_seat_idle_time(check_idle_time)
            max_idle_seat = manage_seats.get_max_idle_seat(check_idle_time)
            avalable_arificial_time = max_idle_seat.idle_duration.start_time


            # 如果不需要人工坐席，产生客户，知道需要人工坐席
            while the_most_urgent_customer==None:
                print('没有坐席需求')
                # 产生客户
                customer_id += 1
                distribution_list = [average_ring_time, average_ring_time2, average_artificial_time]
                prob_list = [prob_success_call, prob_transfer_to_artificial_seat]
                new_customer = Customer.create_a_customer(distribution_list, prob_list, customer_id,
                                                          next_time_create_customer, random_seed=-1)
                all_customers.append(new_customer)

                # 找到最紧急需要人工坐席的客户
                manage_customers = ManageCustomers(all_customers)
                the_most_urgent_customer = manage_customers.get_the_earliest_customer()

                # 计算拨号周期
                if len(all_customers) <= 20000:
                    wait_time = init_customer_wait_time
                    old_flag = -1
                    base_time = next_time_create_customer
                else:
                    new_flag, time_qujian = cal_flag(next_time_create_customer, base_time, update_period=600)
                    if new_flag != old_flag:
                        wait_time = cal_wait_time(all_customers, manage_seats, args.H, F, G)
                        old_flag = new_flag

                next_time_create_customer += datetime.timedelta(seconds=wait_time)


            # 如果有需要人工坐席的客户
            if the_most_urgent_customer!=None:
                print('!!!坐席有需求坐席有需求!!!!')

                # 获取需要人工坐席的时间点
                need_artificial_time = the_most_urgent_customer.customer_tolerance_duration.start_time
                print('0000000000最开始需要人工坐席的时间为：', need_artificial_time, '需要的客户Id:', the_most_urgent_customer.customer_id)
                # 如果需要人工坐席的时间点 大于 下次产生客户的时间点 （可能会产生need_artificial_time更小的cutomer）
                while(need_artificial_time > next_time_create_customer):
                    print('need_artificial_time={} > next_time_create_customer={}   '.format(need_artificial_time, next_time_create_customer), '可能更早的人工坐席需求')
                    customer_id += 1
                    distribution_list = [average_ring_time, average_ring_time2, average_artificial_time]
                    prob_list = [prob_success_call, prob_transfer_to_artificial_seat]
                    new_customer = Customer.create_a_customer(distribution_list, prob_list, customer_id,
                                                              next_time_create_customer, random_seed=-1)
                    all_customers.append(new_customer)

                    #计算拨号周期
                    if len(all_customers) <= 20000:
                        wait_time = init_customer_wait_time
                        old_flag = -1
                        base_time = next_time_create_customer
                    else:
                        new_flag, time_qujian = cal_flag(next_time_create_customer, base_time, update_period=300)
                        if new_flag!=old_flag:
                            wait_time = cal_wait_time(all_customers, manage_seats, args.H, F, G)
                            old_flag = new_flag

                    next_time_create_customer += datetime.timedelta(seconds=wait_time)

                # 更新最紧急需要人工坐席的客户
                print('更新最早需要坐席的客户')
                manage_customers = ManageCustomers(all_customers)
                the_most_urgent_customer = manage_customers.get_the_earliest_customer()
                need_artificial_time = the_most_urgent_customer.customer_tolerance_duration.start_time
                print('111111111更新后需要人工坐席的时间为：', need_artificial_time, '需要的客户Id:', the_most_urgent_customer.customer_id)
                print('不可能有更提前的人工坐席需求', ' next_time_create_customer={}'.format(need_artificial_time), '下次创建的客户id', customer_id+1)

                if need_artificial_time <= next_time_create_customer:
                    print('流程走到这里，有空闲坐席，也有坐席需求  客户转到人工坐席')
                    print('空闲时间最久坐席', max_idle_seat.id, '空闲开始时间:', avalable_arificial_time)
                    print( '紧急客户：',the_most_urgent_customer.customer_id, '需要坐席开始时间:', need_artificial_time, '等待截至时间：',the_most_urgent_customer.customer_tolerance_duration.end_time)

                    # 坐席提前等待客户 必然会产生一个monitor_time_duration
                    if avalable_arificial_time <= need_artificial_time:
                        '''
                        坐席要听7秒再接入
                        need_artificial_time时间未变
                        avalable_arificial_time + 7秒
                        '''
                        monitor_time = min(max(np.random.normal(loc=3, scale=6), 0), 23)#np.random.uniform(4, 12)
                        #监听的时间为 需要坐席时间
                        monitor_time_duration = Duration(start_time=need_artificial_time,duration=monitor_time)

                        avalable_arificial_time2 = monitor_time_duration.end_time

                        # 监听结束后，客户还没挂机
                        if avalable_arificial_time2 < the_most_urgent_customer.customer_tolerance_duration.end_time:
                            the_most_urgent_customer.add_artificial_call(artifical_duration_start_time=avalable_arificial_time2,
                                                                         average_artificial_time=average_artificial_time)
                            the_most_urgent_customer.monitor_time_duration = monitor_time_duration
                            success_trans.append(the_most_urgent_customer)
                        # 监听结束后，客户已经挂机
                        elif avalable_arificial_time2 >= the_most_urgent_customer.customer_tolerance_duration.end_time:
                            print('此客户丢失，产生一个呼损')
                            the_most_urgent_customer.success_transfer_to_artificial_seat = 'unsuccessful'
                            the_most_urgent_customer.monitor_time_duration = monitor_time_duration
                            call_loss_customers.append(the_most_urgent_customer)
                        else:
                            print('逻辑有问题')

                    # 客户需要等待坐席
                    elif avalable_arificial_time > need_artificial_time:
                        # 坐席刚空出，客户已挂机
                        if avalable_arificial_time >= the_most_urgent_customer.customer_tolerance_duration.end_time:
                            print('此客户丢失，产生一个呼损')
                            the_most_urgent_customer.success_transfer_to_artificial_seat = 'unsuccessful'
                            call_loss_customers.append(the_most_urgent_customer)

                        # 坐席监听正在与AI聊天的客户
                        elif avalable_arificial_time < the_most_urgent_customer.customer_tolerance_duration.end_time:
                            monitor_time = min(max(np.random.normal(loc=9, scale=6), 0), 23)#np.random.uniform(4, 12)
                            # 监听的时间为 需要坐席时间
                            monitor_time_duration = Duration(start_time=avalable_arificial_time, duration=monitor_time)

                            avalable_arificial_time2 = monitor_time_duration.end_time

                            # 监听后，客户还没挂机
                            if avalable_arificial_time2 < the_most_urgent_customer.customer_tolerance_duration.end_time:
                                the_most_urgent_customer.add_artificial_call(artifical_duration_start_time=avalable_arificial_time2,
                                                                             average_artificial_time=average_artificial_time)
                                the_most_urgent_customer.monitor_time_duration = monitor_time_duration
                                success_trans.append(the_most_urgent_customer)
                            # 监听后，客户已经挂机
                            elif avalable_arificial_time2 >= the_most_urgent_customer.customer_tolerance_duration.end_time:
                                print('此客户丢失，产生一个呼损')
                                the_most_urgent_customer.success_transfer_to_artificial_seat = 'unsuccessful'
                                monitor_time_duration = Duration(start_time=avalable_arificial_time, end_time=the_most_urgent_customer.customer_tolerance_duration.end_time)
                                the_most_urgent_customer.monitor_time_duration = monitor_time_duration
                                call_loss_customers.append(the_most_urgent_customer)
                            else:
                                print('逻辑有问题')

                    # 将客户交给到坐席
                    if hasattr(the_most_urgent_customer, 'monitor_time_duration'):
                        max_idle_seat.add_a_customer(the_most_urgent_customer)
                        if len(manage_seats.all_artificial_seats[0].call_handled) == 2:
                            cus1 = manage_seats.all_artificial_seats[0].call_handled[0]
                            cus2 = manage_seats.all_artificial_seats[0].call_handled[1]
                            if cus1.success_transfer_to_artificial_seat == 'successful' and cus2.success_transfer_to_artificial_seat == 'successful':
                                print('wait')
                        debug(manage_seats)
                        print('wait')

                print('最早的人工坐席需要时间{} 已处理'.format(need_artificial_time))

        # 如果坐席不空   找到最先空闲的坐席，及其对应的时间点
        else:
            print('找到最先空闲的坐席，及其avalable_arificial_time')
            the_earliest_idle_seat = manage_seats.get_the_earliest_idle_seat()
            last_customer = the_earliest_idle_seat.call_handled[-1]
            if last_customer.success_transfer_to_artificial_seat == 'successful':
                the_earliest_end_time = last_customer.artificial_duration.end_time
            elif last_customer.success_transfer_to_artificial_seat == 'unsuccessful':
                the_earliest_end_time = last_customer.monitor_time_duration.end_time
            avalable_arificial_time = the_earliest_end_time

            # 用坐席可用时间，去更新坐席状态
            check_idle_time = avalable_arificial_time #+datetime.timedelta(seconds=7)
            print('更新前的坐席状态', manage_seats.have_idle_seat)
            print('将空出坐席的时间点为：', check_idle_time)


        print('此次检查结束\n\n')


    success_call_ratio, I, call_loss_ration, need_artificial_seat_ratio = ManageCustomers.cal_C_I_D_ratio(working_customers=all_customers)

    average_artificial_time_cal, busy_ration1, busy_ration2, average_idle_time1, average_idle_time2 = ManageArtificialSeats.cal_busy_ration(manage_seats)

    fitted_distribution(success_trans, call_loss_customers)

    return call_loss_ration, average_artificial_time_cal, busy_ration1, busy_ration2, average_idle_time1, average_idle_time2

if __name__ == '__main__':

    # wait_time_list1 = [0.5*i for i in range(1,70) if 0.5*i<=7]
    # wait_time_list2 = [7 + 0.5*i for i in range(1,70) if 0.5*i<=7]
    # init_customer_wait_time_list = wait_time_list1 + [init_customer_wait_time] + wait_time_list2
    # init_customer_wait_time_list = init_customer_wait_time_list[12:13]
    call_loss_ration_list, busy_ration_list, average_idle_time_list = [],[],[]

    df = pd.DataFrame()
    for customer_num in [5000]:
        for F in [0.5,0.8,1,1.2,1.4,1.6]:
            for G in [0, 1, 2, 3, 4]:
                F = 1
                G = 0
                init_customer_wait_time = 7.16#A * C * I * (1 + D) ** 2 / H / F + G  # 陈凌剑公式
                print('init_customer_wait_time:', init_customer_wait_time)
                # call_loss_ration, busy_ration, average_idle_time, average_real_idle_time = simulation(customer_num, next_time_create_customer, init_customer_wait_time, F, G)
                call_loss_ration, average_artificial_time_cal, busy_ration1, busy_ration2, average_idle_time1, average_idle_time2 = simulation(customer_num, next_time_create_customer, init_customer_wait_time, F, G)

                row = pd.Series({"customer_num":customer_num,
                                 "F":F,
                                 "G":G,
                                 "loss_ration":call_loss_ration,
                                 "average_artificial_time_cal":average_artificial_time_cal,
                                 "busy_ration1":busy_ration1,
                                 "average_idle_time1":average_idle_time1,
                                 "busy_ration2": busy_ration2,
                                 "average_idle_time2": average_idle_time2,
                                 "time":datetime.datetime.now(),
                                 })

                df = df.append(row, ignore_index=True)

                df_filename = 'log.csv'
                if not os.path.exists(df_filename):
                    df.to_csv(df_filename)
                else:
                    df_old = pd.read_csv(df_filename, index_col=0)
                    df = df_old.append(df)
                    df.to_csv(df_filename)

                print('ok')















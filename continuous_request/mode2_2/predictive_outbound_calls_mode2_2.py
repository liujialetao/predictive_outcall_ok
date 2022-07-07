"""
模拟预测试外呼
1 计算拨号周期
2 呼叫模式2：
"""
import datetime
import args
from args import prob_success_call, prob_transfer_to_artificial_seat, average_ring_time, average_ring_time2, average_artificial_time
import numpy as np
from continuous_request.public_configuration import now
from continuous_request.basic_role import Duration, OneOfArtificialSeat, ManageArtificialSeats, ManageCustomers
from continuous_request.other_statistical_analysis import fitted_distribution
from continuous_request.other_statistical_analysis import calculate_dial_interval
from continuous_request.func import CreateSomeCustomers
import pandas as pd
import os

def simulation(customer_num, call_num, seconds_delay, max_wait_time):

    call_loss_customers = []  # 转人工坐席失败的customer
    success_trans = []  # 转人工坐席成功的customer
    # 创建N个人工坐席
    artificial_seats = [OneOfArtificialSeat(i, now) for i in range(args.H)]
    # 管理人工坐席
    manage_seats = ManageArtificialSeats(artificial_seats)
    # 管理所有的customer
    manage_customers = ManageCustomers(all_customers=[], occupy_seat_customers=[])

    next_time_create_customer = now

    CreateSomeCustomers()
    CreateSomeCustomers.create_some_customers(num_of_concurrent =call_num,
                          next_time_create_customer = next_time_create_customer,
                          distribution_list = [average_ring_time, average_ring_time2, average_artificial_time],
                          prob_list = [prob_success_call, prob_transfer_to_artificial_seat],
                          manage_customers = manage_customers
                          )
    print()

    while(manage_customers.all_customers[-1].customer_id < customer_num):

        # 找到最紧急需要人工坐席的客户
        the_most_urgent_customer = manage_customers.get_the_earliest_customer()

        # 计算下次拨号时
        # 上次拨号max_wait_time后，无人转人工
        if the_most_urgent_customer == None:
            next_time_create_customer2 = next_time_create_customer + datetime.timedelta(seconds=max_wait_time)

        elif the_most_urgent_customer!=None:
            # 获取需要人工坐席的时间点
            need_artificial_time = the_most_urgent_customer.customer_tolerance_duration.start_time

            # 上次拨号max_wait_time后，无人转人工
            if (need_artificial_time - next_time_create_customer).total_seconds() > max_wait_time:
                print('距离上次拨号{}秒无客户接入，开始拨号：'.format(max_wait_time))
                next_time_create_customer2 = next_time_create_customer + datetime.timedelta(seconds=max_wait_time)
            else:
                the_earliest_idle_seat = manage_seats.get_the_earliest_idle_seat()
                avalable_arificial_time = the_earliest_idle_seat.find_avalable_arificial_time(now)

                # 坐席提前等待客户 必然会产生一个monitor_time_duration
                if avalable_arificial_time <= need_artificial_time:
                    '''
                    坐席要听7秒再接入
                    need_artificial_time时间未变
                    avalable_arificial_time + 7秒
                    '''
                    monitor_time = min(max(np.random.normal(loc=3, scale=6), 0), 23)  # np.random.uniform(4, 12)
                    # 监听的时间为 需要坐席时间
                    monitor_time_duration = Duration(start_time=need_artificial_time, duration=monitor_time)

                    avalable_arificial_time2 = monitor_time_duration.end_time

                    # 监听结束后，客户还没挂机
                    if avalable_arificial_time2 < the_most_urgent_customer.customer_tolerance_duration.end_time:
                        the_most_urgent_customer.monitor_time_duration = monitor_time_duration
                        the_most_urgent_customer.add_artificial_call(artifical_duration_start_time=avalable_arificial_time2,
                                                                     average_artificial_time=average_artificial_time)
                        success_trans.append(the_most_urgent_customer)
                        next_time_create_customer2 = the_most_urgent_customer.artificial_duration.start_time + datetime.timedelta(seconds=seconds_delay)


                    # 监听结束后，客户已经挂机
                    elif avalable_arificial_time2 >= the_most_urgent_customer.customer_tolerance_duration.end_time:
                        print('计划monitor_time   ', monitor_time_duration.start_time, monitor_time_duration.end_time)
                        print('产生呼损1：坐席提前等待，监听结束后，客户已挂机，客户id：{}'.format(the_most_urgent_customer.customer_id))
                        the_most_urgent_customer.success_transfer_to_artificial_seat = 'unsuccessful'
                        real_monitor_time_duration = Duration(start_time=need_artificial_time, end_time=the_most_urgent_customer.customer_tolerance_duration.end_time)
                        the_most_urgent_customer.monitor_time_duration = real_monitor_time_duration
                        call_loss_customers.append(the_most_urgent_customer)
                        next_time_create_customer2 = next_time_create_customer
                    else:
                        print('逻辑有问题')

                # 客户需要等待坐席
                elif avalable_arificial_time > need_artificial_time:
                    # 等到坐席腾出，客户已挂机
                    if avalable_arificial_time >= the_most_urgent_customer.customer_tolerance_duration.end_time:
                        print('产生呼损2：等到坐席腾出，客户已挂机(无监听过程)，此客户丢失，产生一个呼损，客户id：{}'.format(the_most_urgent_customer.customer_id))
                        the_most_urgent_customer.success_transfer_to_artificial_seat = 'unsuccessful'
                        call_loss_customers.append(the_most_urgent_customer)
                        next_time_create_customer2 = next_time_create_customer
                    # 坐席监听正在与AI聊天的客户
                    elif avalable_arificial_time < the_most_urgent_customer.customer_tolerance_duration.end_time:
                        monitor_time = min(max(np.random.normal(loc=9, scale=6), 0), 23)  # np.random.uniform(4, 12)
                        # 监听的时间为 需要坐席时间
                        monitor_time_duration = Duration(start_time=avalable_arificial_time, duration=monitor_time)

                        avalable_arificial_time2 = monitor_time_duration.end_time

                        # 监听后，客户还没挂机
                        if avalable_arificial_time2 < the_most_urgent_customer.customer_tolerance_duration.end_time:
                            the_most_urgent_customer.monitor_time_duration = monitor_time_duration
                            the_most_urgent_customer.add_artificial_call(
                                artifical_duration_start_time=avalable_arificial_time2,
                                average_artificial_time=average_artificial_time)

                            success_trans.append(the_most_urgent_customer)
                            next_time_create_customer2 = the_most_urgent_customer.artificial_duration.start_time + datetime.timedelta(seconds=seconds_delay)

                        elif avalable_arificial_time2 >= the_most_urgent_customer.customer_tolerance_duration.end_time:
                            print('计划monitor_time   ', monitor_time_duration.start_time, monitor_time_duration.end_time)
                            print('产生呼损3：等到坐席腾出，再监听一会儿，客户已挂机，客户id：{}'.format(the_most_urgent_customer.customer_id))
                            the_most_urgent_customer.success_transfer_to_artificial_seat = 'unsuccessful'
                            real_monitor_time_duration = Duration(start_time=avalable_arificial_time, end_time=the_most_urgent_customer.customer_tolerance_duration.end_time)
                            the_most_urgent_customer.monitor_time_duration = real_monitor_time_duration
                            call_loss_customers.append(the_most_urgent_customer)
                            next_time_create_customer2 = next_time_create_customer
                        else:
                            print('逻辑有问题')

                # 将客户交给到坐席
                if hasattr(the_most_urgent_customer, 'monitor_time_duration'):
                    the_earliest_idle_seat.add_a_customer(the_most_urgent_customer)
                    # 更新坐席状态  目的时让坐席self.have_idle_seat = False  因为刚刚释放的坐坐席，avalable_arificial_time已经被使用了！！！
                    manage_seats.update_have_idle_seat(avalable_arificial_time)
                    print('更新完manage_seats.update_have_idle_seat(avalable_arificial_time)', manage_seats.have_idle_seat)

        if next_time_create_customer2!=next_time_create_customer:
            next_time_create_customer = next_time_create_customer2
            CreateSomeCustomers.create_some_customers(num_of_concurrent=call_num,
                                  next_time_create_customer=next_time_create_customer,
                                  distribution_list=[average_ring_time, average_ring_time2, average_artificial_time],
                                  prob_list=[prob_success_call, prob_transfer_to_artificial_seat],
                                  manage_customers=manage_customers
                                  )
        else:
            print('有呼损，继续寻找紧急客户')

        print()

    print('进度','call_num:',call_num, 'seconds_delay:',seconds_delay, 'max_wait_time:',max_wait_time)
    print(len(manage_customers.all_customers))

    success_call_ratio, I, call_loss_ration, need_artificial_seat_ratio = ManageCustomers.cal_C_I_D_ratio(working_customers=manage_customers.all_customers)

    average_artificial_time_cal, busy_ration1, busy_ration2, average_idle_time1, average_idle_time2 = ManageArtificialSeats.cal_busy_ration(manage_seats)

    fitted_distribution(success_trans, call_loss_customers)

    average_dial_interval = calculate_dial_interval(manage_customers.all_customers)

    return call_loss_ration, average_artificial_time_cal, busy_ration1, busy_ration2, average_idle_time1, average_idle_time2, average_dial_interval

if __name__ == '__main__':

    df = pd.DataFrame()
    for customer_num in [200]:
        for call_num in [2,3,4]:#,4,5,6
            for seconds_delay in [3,6,9,12,15]:
                for max_wait_time in [15,20,25,30]:#20,25,30,35,40
                    print('\n\n进度','call_num:',call_num, 'seconds_delay:',seconds_delay, 'max_wait_time:',max_wait_time)
                    call_loss_ration, average_artificial_time_cal, busy_ration1, busy_ration2, average_idle_time1, average_idle_time2, average_dial_interval = simulation(customer_num, call_num, seconds_delay, max_wait_time)

                    row = pd.Series({"customer_num":customer_num,
                                     "loss_ration":call_loss_ration,
                                     "average_artificial_time_cal":average_artificial_time_cal,
                                     "busy_ration1":busy_ration1,
                                     "average_idle_time1":average_idle_time1,
                                     "busy_ration2": busy_ration2,
                                     "average_idle_time2": average_idle_time2,
                                     "average_dial_interval":average_dial_interval,
                                     "call_num":call_num,
                                     "seconds_delay":seconds_delay,
                                     "max_wait_time":max_wait_time,
                                     "time":datetime.datetime.now(),
                                     })

                    df = df.append(row, ignore_index=True)

    df_filename = 'mode22_200_test9.csv'
    if not os.path.exists(df_filename):
        df.to_csv(df_filename)
    else:
        df_old = pd.read_csv(df_filename, index_col=0)
        df = df_old.append(df)
        df.to_csv(df_filename)
        #         break
        #     break
        # break




















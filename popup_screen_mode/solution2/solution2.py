"""
模拟预测试外呼
1 计算拨号周期
2 呼叫模式2：
"""
import datetime
from popup_screen_mode.public_configuration.args import prob_success_call, prob_transfer_to_artificial_seat, average_ring_time, average_ring_time2, average_artificial_time
from popup_screen_mode.public_configuration import now
from popup_screen_mode.basic_role import OneOfArtificialSeat, ManageArtificialSeats
from popup_screen_mode.basic_role import ManageCustomers
from popup_screen_mode.func import CreateSomeCustomers
from popup_screen_mode.other_statistical_analysis import calculate_dial_interval
import pandas as pd
import numpy as np
import os


def simulation(customer_num, call_num, max_wait_time):
    # 创建N个人工坐席
    artificial_seat = OneOfArtificialSeat(0, start_idle_time=now)

    # 管理所有的customer
    manage_customers = ManageCustomers(all_customers=[], occupy_seat_customers=[])

    # 下次拨号时间
    next_time_create_customer = now

    CreateSomeCustomers()

    call_flag = 1

    next_time_create_customer2 = next_time_create_customer

    trigger_call_batch = [0]
    avalable_arificial_time = now
    while(manage_customers.all_customers==[] or manage_customers.all_customers[-1].customer_id < customer_num):

        if call_flag==1:
            next_time_create_customer = next_time_create_customer2
            # 拨号
            new_customers = CreateSomeCustomers.create_some_customers(num_of_concurrent=call_num,
                                                      next_time_create_customer=next_time_create_customer,
                                                      distribution_list=[average_ring_time, average_ring_time2, average_artificial_time],
                                                      prob_list=[prob_success_call, prob_transfer_to_artificial_seat],
                                                      manage_customers=manage_customers
                                                      )
        # 获取当前的批次号
        now_call_batch_id = manage_customers.all_customers[-1].call_batch

        # 获取下次加入坐席的客户
        next_customer = manage_customers.find_the_next_success_trans_to_seat_customer(avalable_arificial_time)


        # 当前批次的客户
        if next_customer!=None and next_customer.call_batch==now_call_batch_id:

            # 步骤1：加到人工坐席
            next_customer.add_artificial_call(artifical_duration_start_time=next_customer.popup_screen_time[0], average_artificial_time=average_artificial_time)
            artificial_seat.add_a_customer(next_customer)

            # 步骤2：获取坐席可用时间
            avalable_arificial_time = next_customer.artificial_duration.end_time

            # 步骤3：当前触发的批次，记录
            trigger_call_batch.append(next_customer.call_batch)

            # 步骤4：计算下次呼叫实际
            random_time = np.random.uniform(10, 30)
            next_time_create_customer2 = next_customer.artificial_duration.start_time + \
                                         datetime.timedelta(seconds=(min(random_time, next_customer.artificial_duration.duration.total_seconds())))
            print('random_time:', random_time, '\t 聊天时长：',next_customer.artificial_duration.duration.total_seconds())
            print('next_time_create_customer2:', next_time_create_customer2)
            call_flag = 1

        # 不是当前批次的客户
        if next_customer!=None and next_customer.call_batch!=now_call_batch_id:

            # 步骤1：加到人工坐席
            next_customer.add_artificial_call(artifical_duration_start_time=next_customer.popup_screen_time[0],
                                              average_artificial_time=average_artificial_time)
            artificial_seat.add_a_customer(next_customer)

            # 步骤2：获取坐席可用时间
            avalable_arificial_time = next_customer.artificial_duration.end_time
            # 该批次未触发过拨号
            if next_customer.call_batch not in trigger_call_batch:

                # 步骤3：当前触发的批次，记录
                trigger_call_batch.append(next_customer.call_batch)

                # 步骤4：计算下次呼叫实际
                random_time = np.random.uniform(10, 30)
                next_time_create_customer2 = next_customer.artificial_duration.start_time + \
                                             datetime.timedelta(seconds=(min(random_time,
                                                                             next_customer.artificial_duration.duration.total_seconds())))
                print('random_time:', random_time, '\t 聊天时长：',
                      next_customer.artificial_duration.duration.total_seconds())
                print('next_time_create_customer2:', next_time_create_customer2)
                call_flag = 1
            # 该批次触发过拨号  不再拨号
            else:
                call_flag = 0
                print('要不要拨号呢')
                pass

        if next_customer==None:
            # 获取当前批次，外呼全部结束的时间
            latest_costomer, latest_time = manage_customers.get_latest_hang_up_time_mode2(new_customers)
            print('最晚结束的客户id:{}.'.format(latest_costomer.customer_id), '最晚结束时间：{}'.format(latest_time))
            call_flag = 1
            # 如果结束时间小于 最大等待时长   进行下拨呼叫
            if latest_time < next_time_create_customer + datetime.timedelta(seconds=max_wait_time):
                next_time_create_customer2 = latest_time
            else:
                next_time_create_customer2 = next_time_create_customer + datetime.timedelta(seconds=max_wait_time)


        print()


    print('进度','call_num:',call_num, 'seconds_delay:', 'max_wait_time:',max_wait_time)
    print(len(manage_customers.all_customers))

    success_call_ratio, I, call_loss_ration, need_artificial_seat_ratio = ManageCustomers.cal_C_I_D_ratio(working_customers=manage_customers.all_customers)

    manage_seats = ManageArtificialSeats([artificial_seat])
    average_artificial_time_cal, busy_ration, total_idle_time, average_idle_time= ManageArtificialSeats.cal_busy_ration(manage_seats)
    # average_artificial_time_cal, busy_ration1, busy_ration2, average_idle_time1, average_idle_time2 = ManageArtificialSeats.cal_busy_ration([artificial_seat])

    average_dial_interval = calculate_dial_interval(manage_customers.all_customers)

    return call_loss_ration, average_artificial_time_cal, busy_ration, total_idle_time, average_idle_time, average_dial_interval

customer_num = 500
df = pd.DataFrame()
for call_num in [1, 2, 3, 4]:  # ,4,5,6
    for max_wait_time in [40, 50, 60, 70, 80]:  # 20,25,30,35,40
        print('\n\n进度', 'call_num:', call_num, 'max_wait_time:', max_wait_time)
        call_loss_ration, average_artificial_time_cal, busy_ration, total_idle_time, average_idle_time, average_dial_interval = simulation(customer_num, call_num, max_wait_time)
        #
        # row = pd.Series({"customer_num": customer_num,
        #                  "call_num": call_num,
        #                  "max_wait_time": max_wait_time,
        #                  "loss_ration": call_loss_ration,
        #                  "busy_ration":busy_ration,
        #                  "average_idle_time":average_idle_time,
        #                  "average_artificial_time_cal": average_artificial_time_cal,
        #                  "average_dial_interval": average_dial_interval,
        #                  "time": datetime.datetime.now(),
        #                  })
        df_new = pd.DataFrame([{
            "坐席平均聊天时长": average_artificial_time_cal,
            "平均拨号间隔": average_dial_interval,
            "坐席忙占比": busy_ration,
            "模拟客户数量": customer_num,
            "进线时长": average_idle_time,
            "呼损率": call_loss_ration,
            "并发数": call_num,
            "最大等待时间": max_wait_time,
            "实验结束时间": datetime.datetime.now()
        }])

        df = df.append(df_new, ignore_index=True)

    #         df_filename = 'fangan2_3000_test1.csv'
    #         if not os.path.exists(df_filename):
    #             df.to_csv(df_filename)
    #         else:
    #             df_old = pd.read_csv(df_filename, index_col=0)
    #             df = df_old.append(df)
    #             df.to_csv(df_filename)
    #         break
    #     break
    # break
df['呼损率'] = df[u'呼损率'].apply(lambda x: format(x, '.1%'))
df['坐席忙占比'] = df[u'坐席忙占比'].apply(lambda x: format(x, '.1%'))

df_filename = '../result/solution2_test_2_random10-30.csv'
if not os.path.exists(df_filename):
    df.to_csv(df_filename)
else:
    df_old = pd.read_csv(df_filename, index_col=0)
    df = df_old.append(df)
    df.to_csv(df_filename)













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
import os


def simulation(customer_num, T):
    success_trans = []  # 转人工坐席成功的customer
    call_loss_customers = []  # 转人工坐席失败的customer

    # 创建1个人工坐席
    artificial_seat = OneOfArtificialSeat(0, start_idle_time=now)

    # 管理所有的customer
    manage_customers = ManageCustomers(all_customers=[], occupy_seat_customers=[])

    # 下次拨号时间
    next_time_create_customer = now
    # 初始化管理所有客户
    CreateSomeCustomers()
    # 记录坐席可用时间
    avalable_arificial_time = now
    # 第一次腾出坐席的客户id假设为0
    avalable_customer_id = 0

    while(manage_customers.all_customers==[] or manage_customers.all_customers[-1].customer_id < customer_num):

        # 获取下次加入坐席的客户
        the_most_urgent_customer = manage_customers.get_the_earliest_customer()

        while the_most_urgent_customer==None:
            # 产生客户
            CreateSomeCustomers.create_some_customers(num_of_concurrent=1,
                                                      next_time_create_customer=next_time_create_customer,
                                                      distribution_list=[average_ring_time, average_ring_time2,
                                                                         average_artificial_time],
                                                      prob_list=[prob_success_call, prob_transfer_to_artificial_seat],
                                                      manage_customers=manage_customers
                                                      )
            next_time_create_customer = next_time_create_customer+datetime.timedelta(seconds=T)
            # 找到最紧急需要人工坐席的客户
            the_most_urgent_customer = manage_customers.get_the_earliest_customer()

        if the_most_urgent_customer!=None:
            popup_screen_time = the_most_urgent_customer.popup_screen_time[0]
            # 客户需要坐席还有很久，在其后面呼叫的客户，可能更早需要坐席
            while popup_screen_time > next_time_create_customer+datetime.timedelta(seconds=T):
                print('客户需要坐席还有很久，在其后面呼叫的客户，可能更早需要坐席')
                # 产生客户
                CreateSomeCustomers.create_some_customers(num_of_concurrent=1,
                                                          next_time_create_customer=next_time_create_customer,
                                                          distribution_list=[average_ring_time, average_ring_time2,
                                                                             average_artificial_time],
                                                          prob_list=[prob_success_call,
                                                                     prob_transfer_to_artificial_seat],
                                                          manage_customers=manage_customers
                                                          )
                next_time_create_customer = next_time_create_customer+datetime.timedelta(seconds=T)
        # 没有空闲坐席
        if the_most_urgent_customer==None:
            print('逻辑有问题，不可能没有意向客户')

        # 更新最紧急需要人工坐席的客户
        print('更新最早需要坐席的客户')
        the_most_urgent_customer = manage_customers.get_the_earliest_customer()
        popup_screen_time = the_most_urgent_customer.popup_screen_time[0]

        # 有空闲坐席
        if avalable_arificial_time<=popup_screen_time:
            success_trans.append(the_most_urgent_customer)
            print('坐席将由客户id：{}腾出,腾出时间为：{}'.format(avalable_customer_id, avalable_arificial_time))
            # 步骤1：加到人工坐席
            the_most_urgent_customer.add_artificial_call(artifical_duration_start_time=the_most_urgent_customer.popup_screen_time[0], average_artificial_time=average_artificial_time)
            artificial_seat.add_a_customer(the_most_urgent_customer)

            # 步骤2：获取坐席可用时间
            avalable_arificial_time = the_most_urgent_customer.artificial_duration.end_time
            avalable_customer_id = the_most_urgent_customer.customer_id

        # 没有空闲坐席
        else:
            the_most_urgent_customer.success_transfer_to_artificial_seat = 'unsuccessful'
            print('产生呼损的客户id：{}'.format(the_most_urgent_customer.customer_id), '坐席将由客户id：{}腾出,腾出时间为：{}'.format(avalable_customer_id, avalable_arificial_time))
            call_loss_customers.append(the_most_urgent_customer)


        print()
        print()
    print('进度','T:',T)
    print(len(manage_customers.all_customers))

    success_call_ratio, I, call_loss_ration, need_artificial_seat_ratio = ManageCustomers.cal_C_I_D_ratio(working_customers=manage_customers.all_customers)

    manage_seats = ManageArtificialSeats([artificial_seat])
    average_artificial_time_cal, busy_ration, total_idle_time, average_idle_time= ManageArtificialSeats.cal_busy_ration(manage_seats)
    average_dial_interval = calculate_dial_interval(manage_customers.all_customers)

    return call_loss_ration, average_artificial_time_cal, busy_ration, total_idle_time, average_idle_time, average_dial_interval

customer_num = 500
df = pd.DataFrame()
for T in range(6,60,2):
    call_loss_ration, average_artificial_time_cal, busy_ration, total_idle_time, average_idle_time, average_dial_interval = simulation(customer_num, T)

    df_new = pd.DataFrame([{
        "坐席平均聊天时长": average_artificial_time_cal,
        "平均拨号间隔": average_dial_interval,
        "进线时长": average_idle_time,
        "坐席忙占比":busy_ration,
        "呼叫间隔": T,
        "呼损率":call_loss_ration,
        "模拟客户数量": customer_num,
        "实验结束时间": datetime.datetime.now()
    }])

    df = df.append(df_new, ignore_index=True)

    # df_filename = '方案4实验结果_test1.xls'
    # if not os.path.exists(df_filename):
    #     df.to_excel(df_filename)
    # else:
    #     df_old = pd.read_csv(df_filename, index_col=0)
    #     df = df_old.append(df)
    #     df.to_excel(df_filename)
    #         break
    #     break
    # break
df['呼损率'] = df[u'呼损率'].apply(lambda x: format(x, '.1%'))
df['坐席忙占比'] = df[u'坐席忙占比'].apply(lambda x: format(x, '.1%'))

df_filename = '../result/solution4_2.csv'
if not os.path.exists(df_filename):
    df.to_csv(df_filename)
else:
    df_old = pd.read_csv(df_filename, index_col=0)
    df = df_old.append(df)
    df.to_csv(df_filename)













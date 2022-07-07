"""
模拟预测试外呼
1 计算拨号周期
2 呼叫模式2：
"""
import datetime
import args
from args import prob_success_call, prob_transfer_to_artificial_seat, average_ring_time, average_ring_time2, average_artificial_time
import numpy as np
from popup_screen_mode.public_configuration import now
from popup_screen_mode.basic_role import Duration, OneOfArtificialSeat
from popup_screen_mode.basic_role import ManageCustomers
from popup_screen_mode.func import CreateSomeCustomers
import pandas as pd
import os



def simulation(customer_num, call_num, seconds_delay, max_wait_time):
    call_loss_customers = []  # 转人工坐席失败的customer
    success_trans = []  # 转人工坐席成功的customer
    # 创建N个人工坐席
    artificial_seat = OneOfArtificialSeat(id, start_idle_time=now)

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
    # 计算这个批次的最晚挂机时间     所有unkonw的客户中选择
    latest_hang_up_customers = manage_customers.get_latest_batch_customers()
    target_costomer, latest_hang_up_time = manage_customers.get_latest_hang_up_time(latest_hang_up_customers)
    now_call_batch_id = manage_customers.all_customers[-1].call_batch

    while(manage_customers.all_customers[-1].customer_id < customer_num):

        # 找到最紧急需要人工坐席的客户
        the_most_urgent_customer = manage_customers.get_the_earliest_popup_customer()

        # 计算下次拨号时
        # 上次拨号max_wait_time后，无人转人工
        if the_most_urgent_customer == None:
            # 在挂机时间、最大等待时间 中选择最早的时间拨号  不可能有弹屏的情况下！！！ 只能等待最大周期 或者 大家都挂机
            next_time_create_customer2 = min(latest_hang_up_time,  next_time_create_customer+datetime.timedelta(seconds=max_wait_time))

        elif the_most_urgent_customer != None:

            need_artificial_time = the_most_urgent_customer.popup_screen_time[0]

            avalable_arificial_time = artificial_seat.find_avalable_arificial_time(now)
            # 提前空出，成功加入人工坐席
            if avalable_arificial_time <= need_artificial_time:
                if need_artificial_time >= next_time_create_customer+datetime.timedelta(seconds=max_wait_time):
                    print('距离上次拨号{}秒没有弹屏，开始拨号：'.format(max_wait_time))
                    next_time_create_customer2 = next_time_create_customer + datetime.timedelta(seconds=max_wait_time)
                elif need_artificial_time <= next_time_create_customer+datetime.timedelta(seconds=max_wait_time):
                    print('弹屏后转人工后，延迟{}秒再拨号'.format(max_wait_time))
                    the_most_urgent_customer.add_artificial_call(need_artificial_time, average_artificial_time)
                    # 转坐席后的拨号时间计算   待优化点:延迟后的时间要小于最小拨号间隔
                    next_time_create_customer2 = min(the_most_urgent_customer.popup_screen_time[0] + datetime.timedelta(seconds=seconds_delay),
                                                     next_time_create_customer + datetime.timedelta(seconds=max_wait_time))

            # 坐席没空出
            elif avalable_arificial_time > need_artificial_time:
                the_most_urgent_customer.success_transfer_to_artificial_seat = 'unsuccessful'
                call_loss_customers.append(the_most_urgent_customer)

                # 如果在之前的批次出现呼损，从while循环继续执行， 不拨号
                if the_most_urgent_customer.call_batch != now_call_batch_id:
                    print('客户id：{}，非当前批次产生的呼损，批次call_batch:{},继续寻找紧急客户'.format(the_most_urgent_customer.customer_id, the_most_urgent_customer.call_batch))
                    next_time_create_customer2 = next_time_create_customer
                else:
                    print('客户id：{}，当前批次call_batch:{}产生的呼损'.format(the_most_urgent_customer.customer_id, now_call_batch_id))
                    # 找到成功转坐席的最早时间
                    next_success_trans_to_seat_customer,popup_screen_time, target_customer_call_batch = manage_customers.find_the_next_success_trans_to_seat_customer(avalable_arificial_time)

                    print('待完善')
                    # 如果所有的unkonw客户中，没有客户能成功转进坐席
                    if next_success_trans_to_seat_customer == None:
                        # 获取本批次最晚的hang_up_time
                        pass

                    # 如果下个接机的人是在新批次中，则不用考虑 全挂机后的呼叫问题




            # 将客户交给到坐席
            if hasattr(the_most_urgent_customer, 'artificial_duration'):
                artificial_seat.add_a_customer(the_most_urgent_customer)

        if next_time_create_customer2 != next_time_create_customer:
            next_time_create_customer = next_time_create_customer2
            CreateSomeCustomers.create_some_customers(num_of_concurrent=call_num,
                                                      next_time_create_customer=next_time_create_customer,
                                                      distribution_list=[average_ring_time, average_ring_time2, average_artificial_time],
                                                      prob_list=[prob_success_call, prob_transfer_to_artificial_seat],
                                                      manage_customers=manage_customers
                                                      )
            # 计算这个批次的最晚挂机时间     所有unkonw的客户中选择
            latest_hang_up_customers = manage_customers.get_latest_batch_customers()
            target_costomer, latest_hang_up_time = manage_customers.get_latest_hang_up_time(latest_hang_up_customers)
            now_call_batch_id = manage_customers.all_customers[-1].call_batch



        print("len(manage_customers.all_customers):{}".format(len(manage_customers.all_customers)))
        print("len(manage_customers.occupy_seat_customers):{}".format(len(manage_customers.occupy_seat_customers)))
        for customer in manage_customers.occupy_seat_customers:
            print(customer.customer_id, end='\t')
        print('\n')

    print(123)

customer_num = 5000
call_num = 2
max_wait_time = 40
seconds_delay = 15
simulation(customer_num, call_num, seconds_delay, max_wait_time)



















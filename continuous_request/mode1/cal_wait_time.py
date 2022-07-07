import datetime
from continuous_request.basic_role import ManageArtificialSeats, ManageCustomers


def debug(manage_seats):
    # 检查2  每个坐席处理的客户，客户时间上是否有交集
    for artificial_seat in manage_seats.all_artificial_seats:
        artificial_duration_list = []
        for customer in artificial_seat.call_handled:
            if customer.success_transfer_to_artificial_seat == 'successful':
                artificial_duration_list.append((customer.customer_id, customer.monitor_time_duration))
                artificial_duration_list.append((customer.customer_id, customer.artificial_duration))
            elif customer.success_transfer_to_artificial_seat == 'unsuccessful':
                artificial_duration_list.append((customer.customer_id, customer.monitor_time_duration))
            else:
                print('逻辑有问题 检查2  每个坐席处理的客户，客户时间上是否有交集')

        for i in range(len(artificial_duration_list) - 1):
            customer_id1, duration1 = artificial_duration_list[i]
            customer_id2, duration2 = artificial_duration_list[i + 1]

            if duration1.end_time > duration2.start_time:
                print('111逻辑肯定有问题')

        print('ok')
        print('ok')

def cal_flag(next_time_create_customer, base_time, update_period):
    '''
    返回next_time_create_customer落在哪个区间
    '''
    time_interval_list = [(base_time+datetime.timedelta(seconds=update_period*i), (base_time+datetime.timedelta(seconds=update_period*(i+1)))) for i in range(2000)]
    for i in range(1000):
        time_qujian = time_interval_list[i]
        if next_time_create_customer>=time_qujian[0] and next_time_create_customer<time_qujian[1]:
            return i, time_qujian



def cal_wait_time(working_customers, manage_seats, H, F, G):
    '''
    A:人工通话平均时长
    C:电话接通率
    I:转人工比例   I:转人工比例 = 转人工数量/接通数量
    D：坐席接通失败率
    '''
    average_artificial_time_cal, busy_ration1, busy_ration2, average_idle_time1, average_idle_time2  = ManageArtificialSeats.cal_busy_ration(manage_seats)

    A = average_artificial_time_cal

    C, I, D, need_artificial_seat_ratio = ManageCustomers.cal_C_I_D_ratio(working_customers)

    customer_wait_time = A * C * I * (1 + D) ** 2 / H / F + G  # 陈凌剑公式
    print('经计算后customer_wait_time:',customer_wait_time)
    print('I * (1 + D) ** 2  ', I * (1 + D) ** 2)
    return customer_wait_time

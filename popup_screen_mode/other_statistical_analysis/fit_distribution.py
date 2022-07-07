import numpy as np


def fitted_distribution(success_trans, call_loss_customers):
    customer_wait_duration_list = []
    trans_successful_averate_wait_time_list = []
    for customer in success_trans:
        if customer.real_wait_duration != None:
            customer_wait_duration_list.append(customer.customer_id)
            trans_successful_averate_wait_time_list.append(customer.real_wait_duration.duration.total_seconds())
    average_wait_time = np.sum(trans_successful_averate_wait_time_list) / len(success_trans)
    print('成功转接的人，与AI平均聊天时长{:.2f}秒'.format(average_wait_time + 10), '采样值为23.38秒')

    # # 统计成功转接的人，平均忍耐时间
    # customer_tolerance_duration = []
    # for customer in success_trans:
    #     customer_tolerance_duration.append(customer.customer_tolerance_duration.duration.total_seconds())
    # print('成功转接的人，平均忍耐时间为：', np.sum(customer_tolerance_duration) / len(customer_tolerance_duration), '无采样值')

    # 统计未成功转接的人，平均忍耐时间
    customer_tolerance_duration = []
    for customer in call_loss_customers:
        customer_tolerance_duration.append(customer.customer_tolerance_duration.duration.total_seconds())
    print('未成功转接的人，与AI平均聊天时长{:.2f}秒'.format(np.sum(customer_tolerance_duration) / len(call_loss_customers) + 10), '采样值为35.63秒')

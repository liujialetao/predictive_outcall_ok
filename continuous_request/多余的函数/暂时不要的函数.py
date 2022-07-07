def update_customers_status(working_customers, finished_customers, wait_transfer_customers, call_loss_customers, check_time):
    '''
    1
    根据当前检查时间，更新上个时间段在工作中的客户状态
    根据客户状态，将客户分类放入相应列表
    2
    根据当前时间，更新上个状态在等待转人工坐席的客户
    根据客户状态，将客户分类放入相应列表
    '''

    new_working_customers = []
    # 遍历working_customers中的customer状态
    for customer in working_customers:

        customer_status = customer.get_customer_status(check_time)
        # 如果customer在状态1 状态2 状态3， customer放在working_customers中
        if customer_status=='not_start_ring_duration' or customer_status=='ring_duration' or customer_status=='robot_chat_duration' or customer_status=='customer_tolerance_duration' or customer_status=='artificial_seat_duration':
            new_working_customers.append(customer)
        # 如果customer_status包含'over'字段， customer放在finished_customers中  并将
        elif 'over' in customer_status:
            finished_customers.append(customer)

        # 如果customer在状态1 状态2 状态3 状态4
        if customer_status=='customer_tolerance_duration':
            wait_transfer_customers.append(customer)

        if customer_status=='call_loss':
            call_loss_customers.append(customer)

    new_working_customers = list(set(new_working_customers))
    wait_transfer_customers = list(set(wait_transfer_customers))
    return new_working_customers, finished_customers, wait_transfer_customers, call_loss_customers


def updata_working_customers_only(working_customers, finished_customers,check_time):
    '''
    仅根据检查时间点
    更新还在工作的客户
    '''
    new_working_customers = []
    for customer in working_customers:
        customer_status = customer.get_customer_status(check_time)
        if customer_status=='not_start_ring_duration' or customer_status=='ring_duration' or customer_status=='robot_chat_duration' or customer_status=='customer_tolerance_duration' or customer_status=='artificial_seat_duration':
            new_working_customers.append(customer)
        else:
            finished_customers.append(customer)
    return new_working_customers, finished_customers
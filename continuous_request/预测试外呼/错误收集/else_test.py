# '''
# 根据当前的check_time = the_earliest_end_time    将客户加到坐席
# '''
# mange_seats.update_have_idle_seat(check_time)
# if mange_seats.have_idle_seat==False:
#     print('逻辑有问题：此时找到了空闲坐席的时间')
#
# else:
#
# # 更新坐席状态
# mange_seats.update_idle_seat_idle_time(check_time)
#
# max_idle_seat = mange_seats.get_max_idle_seat(check_time)
#
# # 如果转坐席时间，客户已经挂电话
# while (artifical_duration_start_time > the_most_urgent_customer.customer_tolerance_duration.end_time):
#     # 更新客户状态
#     check_time = artifical_duration_start_time
#     customers_working, customers_finished, customers_wait_transfer, customers_call_loss = update_customers_status(
#         customers_working, customers_finished, customers_wait_transfer, customers_call_loss, check_time)
#
#     print('\n')
#
# # 客户转到人工坐席
# print('check_time:开始转转人工坐席', check_time, '紧急客户：', the_most_urgent_customer.customer_id)
# the_most_urgent_customer.add_artificial_call(artifical_duration_start_time=artifical_duration_start_time)
#
# # 将客户的aritificial_duration加入到坐席
# max_idle_seat.add_a_customer(the_most_urgent_customer)
# print('wati333')
#
# # 更新客户状态
# customers_working, customers_finished, customers_wait_transfer, customers_call_loss = update_customers_status(
#     customers_working, customers_finished, customers_wait_transfer, customers_call_loss, check_time)
#
# # 创建实例，找到最紧急需要人工坐席的客服
# manage_working_customers = ManageCustomers(customers_working)
#
# # 周期性检查时间点
# t = now + datetime.timedelta(seconds=T * customer_id)
# # 获取等待时间
# wait_time = int(wait_time_seed[customer_id - 1])  # 待调整
# # 计算下次拨号时间
# next_time_create_customer = t + datetime.timedelta(seconds=wait_time)
# print('wati444')
#
#
# # 接客成功后，
# mange_seats.update_have_idle_seat(check_time)
# if mange_seats.have_idle_seat==True:
#     print('逻辑有问题，接客成功后，')

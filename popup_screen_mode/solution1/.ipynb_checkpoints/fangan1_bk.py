# # 上次拨号max_wait_time后，短期内，无人转人工
# if need_artificial_time > next_time_create_customer+datetime.timedelta(seconds=max_wait_time):
#     # if need_artificial_time >
#     print('距离上次拨号{}秒没有弹屏，开始拨号：'.format(max_wait_time))
#     next_time_create_customer2 = next_time_create_customer + datetime.timedelta(seconds=max_wait_time)
#
# else:
#     avalable_arificial_time = artificial_seat.find_avalable_arificial_time(now)
#     # 提前空出，成功加入人工坐席
#     if avalable_arificial_time <= need_artificial_time:
#         the_most_urgent_customer.add_artificial_call(need_artificial_time, average_artificial_time)
#         next_time_create_customer2 = the_most_urgent_customer.popup_screen_time[0] + datetime.timedelta(seconds=seconds_delay)
#
#     # 坐席没空出
#     elif avalable_arificial_time > need_artificial_time:
#         the_most_urgent_customer.success_transfer_to_artificial_seat = 'unsuccessful'
#         call_loss_customers.append(the_most_urgent_customer)
#         next_time_create_customer2 = next_time_create_customer
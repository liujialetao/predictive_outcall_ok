
# # 与机器人聊天 时间跨度记录
# f_robot_chat_duration = min(max(np.random.normal(loc=average_robot_chat, scale=30), 0), 70)
# self.robot_chat_duration = Duration(start_time=self.ring_duration.end_time,#机器人聊天开始时间
#                                             duration=f_robot_chat_duration
#                                             )
# # 模拟方法1 假设了需要人工坐席和不需要的比例   需要的话，再设置客户容忍度
# # 愿意转人工的概率
# self.need_artificial_seat = np.random.choice(['not_need_artificial_seat', 'need_artificial_seat'], size=1, p=prob_transfer_to_artificial_seat)[0]
# if self.need_artificial_seat=='need_artificial_seat':
#     # 客户等待转人工坐席 时间跨度记录
#     f_maximum_tolerance_time = max(np.random.normal(loc=average_maximum_tolerance, scale=10), 1)
#     self.customer_tolerance_duration = Duration(start_time=self.robot_chat_duration.end_time,
#                                             duration=f_maximum_tolerance_time
#                                             )
#     #转人工成功与否 未知   成功后，修改为'successful' 失败：'unsuccessful'
#     self.success_transfer_to_artificial_seat = 'unknow'

# # 方法2
# # 与机器人聊天 时间跨度记录
# f_robot_chat_duration = min(max(np.random.normal(loc=average_robot_chat, scale=15), 0), 70)
# if f_robot_chat_duration<10:
#     self.robot_chat_duration = Duration(start_time=self.ring_duration.end_time,#机器人聊天开始时间
#                                                 duration=f_robot_chat_duration
#                                                 )
#     self.need_artificial_seat = 'not_need_artificial_seat'
# else:
#     self.robot_chat_duration = Duration(start_time=self.ring_duration.end_time,#机器人聊天开始时间
#                                                 duration=10
#                                                 )
#
# # 模拟方法2  当客户与AI聊天大于10秒后
# if f_robot_chat_duration >= 10:
#     self.need_artificial_seat='need_artificial_seat'
#     f_maximum_tolerance_time = f_robot_chat_duration-10
#     self.customer_tolerance_duration = Duration(start_time=self.robot_chat_duration.start_time+datetime.timedelta(seconds=10),
#                                                 duration=f_maximum_tolerance_time
#                                                )
#     # 转人工成功与否 ‘unknow’   成功后，修改为'successful' 失败：'unsuccessful'
#     self.success_transfer_to_artificial_seat = 'unknow'
# else:
#     self.need_artificial_seat = 'not_need_artificial_seat'
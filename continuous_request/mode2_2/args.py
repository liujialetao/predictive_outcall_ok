import numpy as np

'''
实际拨打数据
通话成功 106
    成功转坐席：31   AI聊天时长7秒
    无空闲坐席：61   AI聊天时长35.7秒
    空白：12 未触发人工坐席需求，例如不想了解这种
    转接中挂断：2
    
静默 22
    AI聊天时长<=10秒：19
    AI聊天时长>10秒：3
'''
#初始化参数，启动服务  初始化参数来自于前天数据或者经验值
C = (106+22)/218
prob_success_call = [1-C, C] #客户 不接听、接听 的概率

want_trans_to_seat = (31+61)/(106+22)
prob_transfer_to_artificial_seat = [1-want_trans_to_seat, want_trans_to_seat] #客户 转人工失败率  成功率

# 用随机函数  模拟振铃时长、机器人聊天时长、客户最大等待人工坐席时长、人工坐席服务时长


# 成功接听的人，振铃时长分布
average_ring_time = 5
# 未成功接听的人，振铃时长分布
average_ring_time2 = 5
# 人工坐席平均聊天时长
average_artificial_time = 27

# 等待时长的公式
A = average_artificial_time #人工平均通话时长
# C = 0.5 # 电话接通率
I = (31)/(106+22) # 转坐席成功率
D = 0.1 # 坐席接通失败率
H = 1 # 人工坐席的个数

# # 与机器人平均聊天时长    经试验，此参数对呼损影响不大
# average_robot_chat = 36

# # 客户等待转到人工坐席的平均时长
# average_maximum_tolerance = 20


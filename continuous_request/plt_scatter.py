import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')
# data1.loss_ration,data1.busy_ration1
call_loss = data1.loss_ration
busy_ration = data1.busy_ration2
call_loss2 = data2.loss_ration
busy_ration2 = data2.busy_ration2

plt.scatter(call_loss, busy_ration, s=100, c='green', marker='*')
plt.scatter(call_loss2, busy_ration2, s=100, c='red', marker='*')
plt.title('result')
plt.xlabel('call_loss_ration')
plt.ylabel('busy_ration')
plt.show()
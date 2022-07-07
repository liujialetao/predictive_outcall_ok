class ZHENGSHU():
    def __init__(self, num):
        self.num = num

list_a = [ZHENGSHU(i) for i in range(5)]

for ele in list_a:
    if ele.num == 3 or ele.num==4:

print(list_a)

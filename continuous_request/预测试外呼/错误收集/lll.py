class A():
    def __init__(self,a,b):
        self.aa = a
        self.bb = b
    def judge(self):
        if hasattr(self, 'aa'):
            print(self.aa)
        else:
            print('meiyou aa')

m = A(3,4)
m.judge()
print('456')

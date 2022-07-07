import datetime比大小,time


def run(tlist):  # 定义方法
    alist = []
    for x in tlist:
        x = x-1
        alist.append(x)
    print(alist)
    time.sleep(1)
    return alist



if __name__ == '__main__':  #
    testlist = [23,34,56,78,90,110]
    print("初始列表值为\n%s"%testlist)
    slist=[]
    for i in range(1,6):
        print("第%d次列表值为"%i)
        slist = run(testlist)
        testlist.clear()
        testlist = slist

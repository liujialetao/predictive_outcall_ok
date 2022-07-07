# https://www.bilibili.com/video/BV1b741157vV?spm_id_from=333.337.search-card.all.click&vd_source=82b424d5825df6f0aeee022464bec1ab
a = 8

def f1():
    print('f1:  ',a)

# def f2():
#     print('f2:  ',a)  # a被认为是局部变量，使用时未定义    UnboundLocalError: local variable 'a' referenced before assignment
#     a = 18

def f3():
    a = 18
    print('f3:  ',a)

def f4():
    global a
    a = 18
    print('f4:  ',a)

f1()
# f2()
f3()
f4()
print('global a:', a)

import datetime比大小  # 导入datetime模块
import threading  # 导入threading模块


def run():  # 定义方法
    print(datetime比大小.datetime比大小.now())  # 输出当前时间
    timer = threading.Timer(1, run)  # 每秒运行
    timer.start()  # 执行方法


if __name__ == '__main__':  #
    t1 = threading.Timer(1, function=run())  # 创建定时器 1就是每隔1秒
    t1.start()  # 开始执行线程
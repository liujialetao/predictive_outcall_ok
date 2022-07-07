import datetime比大小
import threading
import time
import numpy as np

class Timer():
    def __init__(self, survival_time):
        self.survival_time = survival_time
        self.flag = 1

        for i in range(100):
            time.sleep(1)
            self.survival_time = self.survival_time - 1
            if survival_time==0:
                self.flag=0
                break

robots = []
times = [20,30,40,50]
for i in range(len(times)):
    robot = Timer(times[i])
    robots.append(robot)

i=0
while(True):
    print("第%d次"%i)
    for robot in robots:
        print(robot.survival_time,robot.survival_time)
    i+=1
    time.sleep(1)

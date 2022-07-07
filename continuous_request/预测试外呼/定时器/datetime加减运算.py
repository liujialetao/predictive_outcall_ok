import time
import datetime



t1 = datetime.datetime.now()
time.sleep(1.5)
t2 = datetime.datetime.now()
idle_time21 = t2-t1

t3 = datetime.datetime.now()
time.sleep(1.6)
t4 = datetime.datetime.now()
idle_time43 = t4-t3


pass
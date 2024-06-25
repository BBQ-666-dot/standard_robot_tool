'''
StandardRobot++ 上位机主程序
'''
import sys
import os
# 获取当前文件的目录
current_dir = os.path.dirname(__file__)
# 构建到lib目录的相对路径
lib_path = os.path.join(current_dir, 'lib')

sys.path.append(lib_path)

from lib.log_info import LogError , LogInfo , LogWarning
import lib.usb_divice as usb_divice
import threading
import queue
import time
from TASK_UsbDevice import TASK_UsbDevice

LogInfo("开始运行 StandardRobot++ 上位机")

usb = usb_divice.USB_Device()
param_list = [1,2,3,4,5,6,7,8,9,10]

usb_divice_task_thread = threading.Thread(target=TASK_UsbDevice, args=(usb,))
usb_divice_task_thread.start()

# import threading
# import queue
# import time

# def producer(q):
#     for i in range(5):
#         item = f'数据项{i}'
#         q.put(item)
#         print(f'生产者产生了 {item}')
#         time.sleep(1)

# def consumer(q):
#     while True:
#         item = q.get()
#         if item is None:
#             break  # None是停止信号
#         print(f'消费者消费了 {item}')
#         q.task_done()

# # 创建队列实例
# q = queue.Queue()

# # 创建并启动生产者线程
# t1 = threading.Thread(target=producer, args=(q,))
# t1.start()

# # 创建并启动消费者线程
# t2 = threading.Thread(target=consumer, args=(q,))
# t2.start()

# # 等待生产者线程完成
# t1.join()

# # 发送停止信号给消费者线程
# q.put(None)

# # 等待消费者线程完成
# t2.join()
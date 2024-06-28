'''
StandardRobot++ 上位机主程序
'''
import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process

from Window import Window
from OperationTypedef import OPEN_USB,STOP_APP
from TASK_UsbDevice import TASK_UsbDevice
from TASK_Monitor import TASK_Monitor

import threading
import queue
import time

LogInfo("开始运行 StandardRobot++ 上位机")

usb = USB_Device()
data_process = Data_Process()
operation_list = []
run_time = {}


usb_divice_task_thread = threading.Thread(target=TASK_UsbDevice, args=(usb, data_process, operation_list))
usb_divice_task_thread.start()

monitor_task_thread = threading.Thread(target=TASK_Monitor, args=(usb, data_process, operation_list, run_time))
monitor_task_thread.start()

window = Window(usb, data_process, operation_list)

# usb.modify("COM6",9600,8,1,"N")
# operation_list.append(OPEN_USB)
# print(window.operations)



window.InitApp(width=800, height=500)
window.RunApp()


############################################################
#  test
############################################################
usb.modify("COM6",9600,8,1,"N")
operation_list.append(OPEN_USB)
print(window.operations)

# time.sleep(10)
time.sleep(0.1)
operation_list.append(STOP_APP)
print(window.operations)

# LogInfo("结束运行 StandardRobot++ 上位机")

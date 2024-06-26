'''
StandardRobot++ 上位机主程序
'''
import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process
import threading
import queue
import time
from OperationTypedef import OPEN_USB,STOP_APP
from TASK_UsbDevice import TASK_UsbDevice
from TASK_Monitor import TASK_Monitor
from TASK_Window import TASK_Window

LogInfo("开始运行 StandardRobot++ 上位机")

usb = USB_Device()
data_process = Data_Process()
operation_list = []

usb_divice_task_thread = threading.Thread(target=TASK_UsbDevice, args=(usb, data_process, operation_list))
usb_divice_task_thread.start()

monitor_task_thread = threading.Thread(target=TASK_Monitor, args=(usb,operation_list))
monitor_task_thread.start()

window_task_thread = threading.Thread(target=TASK_Window, args=(usb,operation_list))
window_task_thread.start()

############################################################
#  test
############################################################
usb.modify("COM6",9600,8,1,"N")
operation_list.append(OPEN_USB)

time.sleep(2)
operation_list.append(STOP_APP)

# LogInfo("结束运行 StandardRobot++ 上位机")

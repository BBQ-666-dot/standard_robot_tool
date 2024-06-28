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
from TASK_Test import TASK_Test

import threading

LogInfo("开始运行 StandardRobot++ 上位机")

usb = USB_Device()
data_process = Data_Process()
operation_list = []
run_time = {}


usb_divice_task_thread = threading.Thread(target=TASK_UsbDevice, args=(usb, data_process, operation_list, run_time))
usb_divice_task_thread.start()

monitor_task_thread = threading.Thread(target=TASK_Monitor, args=(usb, data_process, operation_list, run_time))
monitor_task_thread.start()

if True:
    test_task_thread = threading.Thread(target=TASK_Test, args=(usb, data_process, operation_list, run_time))
    test_task_thread.start()

window = Window(usb, data_process, operation_list, run_time)

window.InitApp(width=800, height=500)
window.RunApp()


LogInfo("结束运行 StandardRobot++ 上位机")

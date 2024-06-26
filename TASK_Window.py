import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
import threading
import time
from OperationTypedef import OPEN_USB,CLOSE_USB,STOP_APP

def TASK_Window(usb:USB_Device, oprations:list):
    LogInfo("开始运行 StandardRobot++ 上位机的交互窗口模块")

    while True:
        #处理操作
        if len(oprations)>0 and oprations[0] == STOP_APP:
            break #stop app

        time.sleep(0.1)
    
    LogInfo("结束运行 StandardRobot++ 上位机的交互窗口模块")

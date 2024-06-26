import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
import time
from OperationTypedef import STOP_APP


def TASK_Monitor(usb:USB_Device, oprations:list):
    LogInfo("开始运行 StandardRobot++ 上位机的监测模块")

    while True:
        #处理操作
        if len(oprations)>0 and oprations[0] == STOP_APP:
            break #stop app

        LogInfo(f"usb_open:{usb.is_open}")
        time.sleep(1)
    
    LogInfo("结束运行 StandardRobot++ 上位机的监测模块")

import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process

import time
from OperationTypedef import OPEN_USB,STOP_APP,ERROR

def TASK_Test(usb:USB_Device, data_process:Data_Process, oprations:list, run_time:dict):
    LogInfo("开始运行 StandardRobot++ 上位机的测试模块")
    
    usb.modify("COM6",9600,8,1,"N")
    oprations.append(OPEN_USB)
    
    cnt = 0
    while True:
        #处理操作
        if len(oprations)>0 and (oprations[0] == STOP_APP or (ERROR in oprations)):
            break
        
        cnt += 1
        if cnt == 200:
            oprations.append(ERROR)
        time.sleep(0.01)
    
    LogInfo("结束运行 StandardRobot++ 上位机的测试模块")
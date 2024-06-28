import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process

import time
from OperationTypedef import STOP_APP,ERROR


def TASK_Monitor(usb:USB_Device, data_process:Data_Process, oprations:list, run_time:dict):
    LogInfo("开始运行 StandardRobot++ 上位机的监测模块")
    
    start_time = int(time.time() * 1000)
    start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + f".{int(time.time() % 1 * 1000):03d}"
    LogInfo(f"Start time str: {start_time_str}")
    LogInfo(f"Start time: {start_time}")

    while True:
        #处理操作
        if len(oprations)>0 and oprations[0] == STOP_APP:
            break #stop app
        
        data_process.imu_data.limit(500)
        data_process.debug_data.limit(5000)
        
        LogInfo(f"storage_len:{len(data_process.imu_data.storage['time_stamp'])}")
        LogInfo(f"oprations:{oprations}")
        
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + f".{int(time.time() % 1 * 1000):03d}"
        current_time = int(time.time() * 1000)
        LogInfo(f"Current time str: {current_time_str}")
        LogInfo(f"Current time: {current_time}")
        LogWarning(f"Time interval: {current_time - start_time}")

        
        time.sleep(1)
    
    LogInfo("结束运行 StandardRobot++ 上位机的监测模块")

if __name__ == '__main__':
    usb = USB_Device()
    data_process = Data_Process()
    operation_list = []
    run_time = {}
    
    TASK_Monitor(usb, data_process, operation_list, run_time)
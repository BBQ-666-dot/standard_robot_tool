import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process

import time
from OperationTypedef import STOP_APP,ERROR

tasks = ["TASK_UsbDevice",
         "TASK_Monitor",
         "TASK_Window",
         "TASK_Listen",
         "TASK_UsbSend",
         ]

def TASK_Monitor(usb:USB_Device, data_process:Data_Process, oprations:list, run_time:dict):
    start_time = int(time.time() * 1000)
    run_time['TASK_Monitor'] = start_time
    LogInfo(f"[{start_time}(ms)]开始运行 StandardRobot++ 上位机的监测模块")
    
    time.sleep(0.5) #等待其他线程启动

    while True:
        #处理操作
        if len(oprations)>0 and (oprations[0] == STOP_APP or (ERROR in oprations)):
            break #stop app
        
        data_process.imu_data.limit(500)
        data_process.debug_data.limit(5000)
        
        LogInfo(f"usb_state:{ '打开'if usb.is_open else '关闭'}")
        LogInfo(f"oprations:{oprations}")
        
        current_time = int(time.time() * 1000)
        run_time['TASK_Monitor'] = current_time
        for key in tasks:
            task_run_time = run_time.get(key,0)
            delta_time = current_time - task_run_time
            if delta_time < 1500:
                LogInfo(f"[{start_time}(ms)] {key} 运行正常")
            else:
                LogWarning(f"[{start_time}(ms)] {key} 运行异常")
                oprations.append(ERROR)
        
        time.sleep(1)
    
    if usb.is_open:
        usb.close()
    LogInfo("结束运行 StandardRobot++ 上位机的监测模块")

if __name__ == '__main__':
    usb = USB_Device()
    data_process = Data_Process()
    operation_list = []
    run_time = {}
    
    TASK_Monitor(usb, data_process, operation_list, run_time)
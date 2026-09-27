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

    strikes = {key: 0 for key in tasks}
    reported = {key: False for key in tasks}
    cnt = 0
    while True:
        #处理操作
        if len(oprations)>0 and oprations[0] == STOP_APP:
            break #stop app
        
        data_process.imu_data.limit(500)
        data_process.debug_data.limit(5000)
        
        current_time = int(time.time() * 1000)
        run_time['TASK_Monitor'] = current_time

        # 任务看门狗: 连续3次(3s)未上报才算异常, 只记录日志, 不停止其他线程
        for key in tasks:
            # 串口开/关操作可能耗时较长(某些蓝牙/虚拟串口要几秒), 期间不判异常
            if key == 'TASK_UsbDevice' and len(oprations) > 0:
                strikes[key] = 0
                continue
            delta_time = current_time - run_time.get(key, 0)
            if delta_time >= 1500:
                strikes[key] += 1
                if strikes[key] >= 3 and not reported[key]:
                    reported[key] = True
                    LogError(f"{key} 运行异常({delta_time}ms)，请检查对应功能")
            else:
                if reported[key]:
                    LogInfo(f"{key} 已恢复正常")
                strikes[key] = 0
                reported[key] = False

        # 正常状态每20s汇总一次，避免日志刷屏
        cnt += 1
        if cnt % 20 == 0:
            LogInfo(f"usb_state:{ '打开' if usb.is_open else '关闭'}  oprations:{oprations}")

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
import AddLib
AddLib.add_lib()

from OperationTypedef import OPEN_USB,CLOSE_USB,STOP_APP,ERROR
from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process
from lib.data_typedef import SEND_ID_ROBOT_CMD
import lib.CRC8_CRC16 as crc

import threading
import time

def TASK_UsbSend(usb:USB_Device, data_process:Data_Process, oprations:list, run_time:dict, robot_cmd:dict):
    start_time = int(time.time() * 1000)
    run_time['TASK_UsbSend'] = start_time
    LogInfo(f"[{start_time}(ms)]开始运行 StandardRobot++ 上位机的USB数据发送模块")
    
    while True:
        current_time = int(time.time() * 1000)
        run_time['TASK_UsbSend'] = current_time # 喂狗
        
        #处理操作
        if len(oprations)>0:
            if oprations[0] == STOP_APP or (ERROR in oprations):
                break #stop app
        
        data_process.robot_cmd_data.update(robot_cmd)
        
        if data_process.sending_data:
            if usb.is_open:
                data = data_process.send(SEND_ID_ROBOT_CMD)
                usb.send(data)
                # print(data)
                # print(len(data))
                # print(current_time)
        
        time.sleep(0.001)


if __name__ == '__main__':
    usb = USB_Device()
    data_process = Data_Process()
    oprations = []
    run_time = {}
    robot_cmd = {
                'time_stamp': 0,
                'speed_vector': {
                        'vx': 3,
                        'vy': 3,
                        'wz': 3,
                        },
                'chassis': {
                        'roll': 2,
                        'yaw': 1,
                        'pitch': 0,
                        'leg_length': 5,
                        },
                'gimbal': {
                        'yaw': 4,
                        'pitch': 2,
                        },
                'shoot': {
                        'fire': 1,
                        'fric_on': 1,
                        },
            }

    usb_divice_task_thread = threading.Thread(target=TASK_UsbSend, args=(usb,data_process,oprations,run_time,robot_cmd))
    usb_divice_task_thread.start()
    
    usb.get()
    usb.modify("COM6",9600,8,1,"N")
    usb.open()
    time.sleep(0.01)
    data_process.start_send()
    
    time.sleep(3)
    oprations.append(STOP_APP)
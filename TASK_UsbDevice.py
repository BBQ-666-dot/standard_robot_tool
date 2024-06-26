'''
StandardRobot++ 上位机的USB通信模块
'''
import sys
import os
# 获取当前文件的目录
current_dir = os.path.dirname(__file__)
# 构建到lib目录的相对路径
lib_path = os.path.join(current_dir, 'lib')

sys.path.append(lib_path)

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
import threading
import time
from OperationTypedef import OPEN_USB,CLOSE_USB,STOP_APP

def TASK_UsbDevice(usb:USB_Device, oprations:list):
    '''
    usb: USB设备
    oprations: 操作列表
    '''
    LogInfo("开始运行 StandardRobot++ 上位机的USB通信模块")
    
    usb.get()
    
    while True:
        #处理操作
        if len(oprations)>0:
            if oprations[0] == OPEN_USB:
                usb.open()
                oprations.pop(0)
            elif oprations[0] == CLOSE_USB:
                usb.close()
                oprations.pop(0)
            elif oprations[0] == STOP_APP:
                break #stop app
        
        if usb.is_open:
            data=usb.read(30)
            print(data)
        else:
            pass
        
        # 任务延时
        # time.sleep(0.001) # Sleep for 1ms
        time.sleep(0.1)

    if usb.is_open:
        usb.close()
    LogInfo("结束运行 StandardRobot++ 上位机的USB通信模块")

if __name__ == '__main__':
    usb = USB_Device()
    oprations = []
    
    usb_divice_task_thread = threading.Thread(target=TASK_UsbDevice, args=(usb,oprations))
    usb_divice_task_thread.start()
    
    usb.modify("COM11",200,8,1,"N")
    oprations.append(OPEN_USB)


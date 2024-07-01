'''
StandardRobot++ 上位机的USB通信模块
'''
import AddLib
AddLib.add_lib()

from OperationTypedef import OPEN_USB,CLOSE_USB,STOP_APP,ERROR
from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process
import lib.CRC8_CRC16 as crc
import threading
import time

def TASK_UsbDevice(usb:USB_Device, data_process:Data_Process, oprations:list, run_time:dict):
    '''
    usb: USB设备
    oprations: 操作列表
    '''
    
    start_time = int(time.time() * 1000)
    run_time['TASK_UsbDevice'] = start_time
    LogInfo(f"[{start_time}(ms)]开始运行 StandardRobot++ 上位机的USB通信模块")
    time.sleep(0.001)

    
    usb.get()
    
    while True:
        current_time = int(time.time() * 1000)
        run_time['TASK_UsbDevice'] = current_time
        
        #处理操作
        if len(oprations)>0:
            if oprations[0] == OPEN_USB:
                usb.open()
                oprations.pop(0)
            elif oprations[0] == CLOSE_USB:
                usb.close()
                oprations.pop(0)
            elif oprations[0] == STOP_APP or (ERROR in oprations):
                break #stop app
        
        if usb.is_open:
            if usb.buf_is_empty():
                time.sleep(0.001)
                continue
            received_data = b''
            data = b''
            #读取帧头的第一个字节
            while data != b'\x5a' and usb.is_open:
                data = usb.read(1)
                received_data += data
            #读取帧头剩余的3个字节
            data = usb.read(3)
            received_data += data
            crc_ok = crc.VerifyCRC8(received_data)
            if crc_ok:            
                data_len = int(received_data[1])
            
                data = usb.read(data_len+2)
                received_data += data
                crc_ok = crc.VerifyCRC16(received_data)
                if crc_ok:
                    data_process.receive(received_data)
        else:
            time.sleep(0.001)

    if usb.is_open:
        usb.close()
    LogInfo("结束运行 StandardRobot++ 上位机的USB通信模块")

if __name__ == '__main__':
    usb = USB_Device()
    data_process = Data_Process()
    oprations = []
    run_time = {}
    
    usb_divice_task_thread = threading.Thread(target=TASK_UsbDevice, args=(usb,data_process,oprations,run_time))
    usb_divice_task_thread.start()
    
    usb.modify("COM6",9600,8,1,"N")
    oprations.append(OPEN_USB)
    
    time.sleep(3)
    oprations.append(STOP_APP)


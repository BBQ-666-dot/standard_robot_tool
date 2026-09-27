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

def _read_exact(usb, size, timeout=0.1) -> bytes:
    '''读取指定长度的数据(带超时, 避免阻塞线程)'''
    buf = b''
    t0 = time.time()
    while len(buf) < size and usb.is_open:
        chunk = usb.read(size - len(buf))
        if chunk:
            buf += chunk
        else:
            if time.time() - t0 > timeout:
                break
            time.sleep(0.001)
    return buf


def TASK_UsbDevice(usb:USB_Device, data_process:Data_Process, oprations:list, run_time:dict):
    '''
    usb: USB设备
    oprations: 操作列表
    '''
    
    start_time = int(time.time() * 1000)
    run_time['TASK_UsbDevice'] = start_time
    LogInfo(f"[{start_time}(ms)]开始运行 StandardRobot++ 上位机的USB通信模块")
    time.sleep(0.003)

    
    usb.get()
    
    while True:
        current_time = int(time.time() * 1000)
        run_time['TASK_UsbDevice'] = current_time
        
        #处理操作
        if len(oprations)>0:
            if oprations[0] == OPEN_USB:
                run_time['TASK_UsbDevice'] = int(time.time() * 1000) #打开端口可能较慢, 先喂狗
                usb.open()
                run_time['TASK_UsbDevice'] = int(time.time() * 1000)
                oprations.pop(0)
            elif oprations[0] == CLOSE_USB:
                usb.close()
                oprations.pop(0)
            elif oprations[0] == STOP_APP:
                break #stop app
        
        if usb.is_open:
            if usb.buf_is_empty():
                time.sleep(0.003)
                continue

            received_data = b''
            data = b''
            #读取帧头的第一个字节(等待数据时也能响应关闭端口等操作)
            while usb.is_open and len(oprations) == 0 and data != b'\x5a':
                data = usb.read(1)
                if not data:
                    time.sleep(0.002)
                    continue
                received_data += data
            if data != b'\x5a':
                continue

            #读取帧头剩余的3个字节
            received_data += _read_exact(usb, 3)
            crc_ok = crc.VerifyCRC8(received_data)
            if crc_ok:
                data_len = int(received_data[1])
                received_data += _read_exact(usb, data_len + 2)
                crc_ok = crc.VerifyCRC16(received_data)
                if crc_ok:
                    data_process.receive(received_data)
                    data_process.stats['rx_frames'] += 1
                else:
                    data_process.stats['rx_errors'] += 1
            else:
                data_process.stats['rx_errors'] += 1
        else:
            time.sleep(0.003)

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


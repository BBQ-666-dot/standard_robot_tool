import serial
import serial.tools.list_ports
import CRC8_CRC16 as crc
from log_info import LogError , LogInfo , LogWarning

class USB_Device:
    def __init__(self):
        self.ser = serial.Serial()
        self.is_open = False
        
        self.port     = None #端口
        self.baudrate = 9600 #波特率    9600
        self.bytesize = 8    #字节大小  8
        self.stopbits = 1    #停止位    1
        self.parity   = "N"  #校验位 N－无校验，E－偶校验，O－奇校验
        
############################################################
#  串口基本功能
#  open
#  close
#  get
#  modify
#  buf_is_empty
#  clear_rx_buf
############################################################
    
    def open(self) -> bool:
        if(self.ser.isOpen()):
            LogWarning("USB已经打开！")
            LogError("USB打开失败！")
            return False

        self.ser.port=self.port         #端口
        self.ser.baudrate=self.baudrate #波特率    9600
        self.ser.bytesize=self.bytesize #字节大小  8
        self.ser.stopbits=self.stopbits #停止位    1
        self.ser.parity=self.parity     #校验位 N－无校验，E－偶校验，O－奇校验
        try:
            self.ser.open()
        except:
            LogError(f"USB打开失败！")
            return False

        if(self.ser.isOpen()):
            LogInfo("USB打开成功！")
            self.is_open = True
            return True
        else:
            LogError("USB打开失败！")

    def close(self) -> bool:
        self.ser.close()
        if(self.ser.isOpen()):
            LogError("USB关闭失败！")
            return False
        else:
            LogInfo("USB关闭成功！")
            self.is_open = False
            return True
        
    def get(self) -> list:
        ports = serial.tools.list_ports.comports()
        if len(ports) == 0:
            LogWarning("未找到USB设备！")
        
        for port in ports:
            LogInfo(port)
            
        return ports

    def modify(self, port:str, baudrate:int=9600, bytesize:int=8, stopbits:int=1, parity:str="N") -> bool:
        if self.is_open:
            LogWarning("USB已经打开！")
            LogError("USB设备信息更新失败！")
            return False
        self.port=port         #端口
        self.baudrate=baudrate #波特率    9600
        self.bytesize=bytesize #字节大小  8
        self.stopbits=stopbits #停止位    1
        self.parity=parity     #校验位 N－无校验，E－偶校验，O－奇校验
        LogInfo("USB设备信息已更新！")
        return True
    
    def buf_is_empty(self) -> bool:
        if self.ser.in_waiting == 0:
            return True
        else:
            return False
    
    def clear_rx_buf(self):
        self.ser.reset_input_buffer()
        LogInfo("接收缓存区已清空！")
        

############################################################
#  串口数据收发
#  read
############################################################
    
    def read(self, size:int) -> bytes:
        data = self.ser.read(size)
        return data


if __name__ == '__main__':
    import struct
    import time
    
    usb = USB_Device()
    usb.get()
    usb.modify(port = "COM11")
    usb.open()
    for _ in range(10):
        received_data = b''
        data = b''
        #读取帧头的第一个字节
        while data != b'\x5a':
            data = usb.read(1)
            print('data=',data)
            received_data += data
        #读取帧头剩余的3个字节
        data = usb.read(3)
        received_data += data
        print('received=',received_data)
        crc8 = crc.GetCRC8(received_data[:-1])
        print('crc8_calc=',crc8)
        print('crc8_recv=',list(received_data)[-1])
        print('crc8_ok=',crc.VerifyCRC8(received_data))
        
        data_len = int(received_data[1])
        data_id = int(received_data[2])
        LogInfo("接收到数据,数据长度为%d,数据ID为%d"%(data_len,data_id))
        data = usb.read(data_len+2)
        received_data += data
        crc16 = crc.GetCRC16(received_data[:-2])
        print('received=',received_data)
        print('crc16_calc=',crc16)
        uint16_int = struct.unpack('<H', received_data[-2:])[0]  # '<H'表示小端模式的无符号短整型
        print('crc16_recv=', uint16_int)
        print('crc16_ok=',crc.VerifyCRC16(received_data))
        if usb.ser.in_waiting == 0:
            print("接收缓存区为空")
        else:
            print("接收缓存区不为空")
        usb.clear_rx_buf()
        if usb.ser.in_waiting == 0:
            print("接收缓存区为空")
        else:
            print("接收缓存区不为空")
        
        time.sleep(1)
    
    usb.close()
    
    

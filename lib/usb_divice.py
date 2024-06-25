import serial
import serial.tools.list_ports
import CRC8_CRC16 as crc
from log_info import LogError , LogInfo , LogWarning

class USB_Device:
    def __init__(self):
        self.ser = serial.Serial()
        self.is_open = False
        
############################################################
#  串口基本功能
#  OpenPort
#  ClosePort
#  GetPort
############################################################
    
    def OpenPort(self, port:str, baudrate:int=9600, bytesize:int=8, stopbits:int=1, parity:str="N") -> bool:
        if(self.ser.isOpen()):
            LogWarning("串口已经打开！")
            LogError("串口打开失败！")
            return False

        self.ser.port=port         #端口
        self.ser.baudrate=baudrate #波特率    9600
        self.ser.bytesize=bytesize #字节大小  8
        self.ser.stopbits=stopbits #停止位    1
        self.ser.parity=parity     #校验位 N－无校验，E－偶校验，O－奇校验
        try:
            self.ser.open()
        except:
            LogError(f"串口打开失败！")
            return False

        if(self.ser.isOpen()):
            LogInfo("串口打开成功！")
            self.is_open = True
            return True
        else:
            LogError("串口打开失败！")

    def ClosePort(self) -> bool:
        self.ser.close()
        if(self.ser.isOpen()):
            LogError("串口关闭失败！")
            return False
        else:
            LogInfo("串口关闭成功！")
            self.is_open = False
            return True
        
    def GetPort(self) -> list:
        ports = serial.tools.list_ports.comports()
        if len(ports) == 0:
            LogWarning("未找到串口！")
        
        for port in ports:
            LogInfo(port)
            
        return ports

############################################################
#  串口数据收发
#  ReadData
############################################################
    
    def ReadData(self, size:int) -> bytes:
        data = self.ser.read(size)
        return data


if __name__ == '__main__':
    import struct
    
    usb = USB_Device()
    usb.GetPort()
    usb.OpenPort("COM11")
    
    received_data = b''
    data = b''
    #读取帧头的第一个字节
    while data != b'\x5a':
        data = usb.ReadData(1)
        print('data=',data)
        received_data += data
    #读取帧头剩余的3个字节
    data = usb.ReadData(3)
    received_data += data
    print('received=',received_data)
    crc8 = crc.GetCRC8(received_data[:-1])
    print('crc8_calc=',crc8)
    print('crc8_recv=',list(received_data)[-1])
    print('crc8_ok=',crc.VerifyCRC8(received_data))
    
    data_len = int(received_data[1])
    data_id = int(received_data[2])
    LogInfo("接收到数据,数据长度为%d,数据ID为%d"%(data_len,data_id))
    data = usb.ReadData(data_len+2)
    received_data += data
    crc16 = crc.GetCRC16(received_data[:-2])
    print('received=',received_data)
    print('crc16_calc=',crc16)
    uint16_int = struct.unpack('<H', received_data[-2:])[0]  # '<H'表示小端模式的无符号短整型
    print('crc16_recv=', uint16_int)
    print('crc16_ok=',crc.VerifyCRC16(received_data))
    
    
    usb.ClosePort()
    
    

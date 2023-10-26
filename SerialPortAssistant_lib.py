"""
串口助手的部分功能函数库

"""
import serial
import struct
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# plt.rcParams['font.family'] = ['SimHei']  # replace with your installed Chinese font
import datetime as dt
import numpy as np
import os
import sys

# INT = 0
UINT32_T = 0 #指代uint32类型的数据
FLOAT = 1    #指代float类型的数据
# UINT8_T = 2
# UINT16_T = 3


READ_FAILED = 0       #读取失败
READ_SUCCESSFULLY = 1 #读取成功
READ_CRC_ERROR = 2    #CRC校验失败
READ_HEADER_ERROR = 3 #header校验失败

SEND_FAILED = 0       #发送失败
SEND_SUCCESSFULLY = 1 #发送成功

WORD_COUNT = 10 #数据名称的字节数

# CRC16校验表
W_CRC_TABLE = [
  0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf, 0x8c48, 0x9dc1, 0xaf5a, 0xbed3,
  0xca6c, 0xdbe5, 0xe97e, 0xf8f7, 0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
  0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876, 0x2102, 0x308b, 0x0210, 0x1399,
  0x6726, 0x76af, 0x4434, 0x55bd, 0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
  0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c, 0xbdcb, 0xac42, 0x9ed9, 0x8f50,
  0xfbef, 0xea66, 0xd8fd, 0xc974, 0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
  0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3, 0x5285, 0x430c, 0x7197, 0x601e,
  0x14a1, 0x0528, 0x37b3, 0x263a, 0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
  0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9, 0xef4e, 0xfec7, 0xcc5c, 0xddd5,
  0xa96a, 0xb8e3, 0x8a78, 0x9bf1, 0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
  0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70, 0x8408, 0x9581, 0xa71a, 0xb693,
  0xc22c, 0xd3a5, 0xe13e, 0xf0b7, 0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
  0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036, 0x18c1, 0x0948, 0x3bd3, 0x2a5a,
  0x5ee5, 0x4f6c, 0x7df7, 0x6c7e, 0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
  0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd, 0xb58b, 0xa402, 0x9699, 0x8710,
  0xf3af, 0xe226, 0xd0bd, 0xc134, 0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
  0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3, 0x4a44, 0x5bcd, 0x6956, 0x78df,
  0x0c60, 0x1de9, 0x2f72, 0x3efb, 0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
  0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a, 0xe70e, 0xf687, 0xc41c, 0xd595,
  0xa12a, 0xb0a3, 0x8238, 0x93b1, 0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
  0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330, 0x7bc7, 0x6a4e, 0x58d5, 0x495c,
  0x3de3, 0x2c6a, 0x1ef1, 0x0f78]



txt_to_type = {
    'float': FLOAT,
    'int': UINT32_T,
}
type_to_txt = {
    FLOAT: 'float',
    UINT32_T: 'int',
}


def App_path():
    """获得主程序的路径"""
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)  #使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__)            #没打包前的py目录


def mkdir(path):
    """创建文件夹目录"""
    isExists = os.path.exists(path)
    if not isExists:# 如果不存在则创建目录
        os.makedirs(path)# 创建目录操作函数
        

def BinaryToFloat(raw_binary_data):
    return struct.unpack('!f', raw_binary_data[::-1])[0]  # 解析二进制数据为浮点数
    

def BinaryArrayToName(binary_array: bytes):
    '''现阶段只支持英文'''
    if binary_array[0] == 0:
        return None
    pos = binary_array.find(b'\x00')
    if pos == -1:
        return binary_array.decode('utf-8')
    else:
        return binary_array[:pos].decode('utf-8')
    
    
                    
class RealTimePlot_2D:
    def __init__(self, ax):
        self.ax = ax
        
        self.ax._button_pressed = False
        self.ax._button_press_event = None
        self.ax._dragging = False
        self.ax._drag_start = (0, 0)
        self.ax._zoom_scale = 1.0
        self.ax._move_position = (0, 0)
        
        self.mouse_prev_pos = None
        self.ax_prev_lim = None
        self.center_after_offset = (0, 0)
        
        self.x = []
        self.y = []
        self.title = ''
        self.x_label = ''
        self.y_label = ''
        
    def update_plot(self):
        self.ax.cla()
        self.ax.plot(self.x, self.y)
        
        self.ax.set_title(self.title, fontsize=15)  # 添加标题
        self.ax.set_xlabel(self.x_label, fontsize=15)  # 添加X轴标签
        self.ax.set_ylabel(self.y_label, fontsize=15)  # 添加X轴标签
        self.ax.grid(True)  # 添加网格线


        return
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        if self.ax_prev_lim == None:
            self.ax_prev_lim = (xlim, ylim)
        x_center = 0.5 * (self.ax_prev_lim[0][0] + self.ax_prev_lim[0][1]) + self.ax._move_position[0]
        y_center = 0.5 * (self.ax_prev_lim[1][0] + self.ax_prev_lim[1][1]) + self.ax._move_position[1]
        x_width = xlim[1] - xlim[0]
        y_width = ylim[1] - ylim[0]
        new_x_width = x_width * self.ax._zoom_scale
        new_y_width = y_width * self.ax._zoom_scale
        self.ax.set_xlim(x_center - 0.5 * new_x_width, x_center + 0.5 * new_x_width)
        self.ax.set_ylim(y_center - 0.5 * new_y_width, y_center + 0.5 * new_y_width)
    
    def on_button_press(self, event):
        if event.button == 1:
            self.ax._button_pressed = True
            self.ax._button_press_event = event
        elif event.button == 3:
            self.ax._dragging = True
            self.ax._drag_start = (event.x, event.y)
        self.mouse_prev_pos = (event.x, event.y)
    
    def on_button_release(self, event):
        if event.button == 1:
            self.ax._button_pressed = False
        elif event.button == 3:
            self.ax._dragging = False
        self.mouse_prev_pos = None
        self.ax_prev_lim = None
    
    def on_mouse_move(self, event):
        if self.ax._button_pressed:
            if self.mouse_prev_pos is None:
                self.mouse_prev_pos = (event.x, event.y)
            dx = event.x - self.mouse_prev_pos[0]
            dy = event.y - self.mouse_prev_pos[1]
            self.mouse_prev_pos = (event.x, event.y)
            dx /= 500
            dy /= 5000

            self.ax._move_position = (self.ax._move_position[0]+dx, self.ax._move_position[1]+dy)
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            # if self.ax_prev_lim == None:
            self.ax_prev_lim = (xlim, ylim)
            
            x_center = 0.5 * (xlim[0] + xlim[1]) + self.ax._move_position[0]
            y_center = 0.5 * (ylim[0] + ylim[1]) + self.ax._move_position[1]
            x_width = xlim[1] - xlim[0]
            y_width = ylim[1] - ylim[0]
            new_x_width = x_width * self.ax._zoom_scale
            new_y_width = y_width * self.ax._zoom_scale
            self.ax.set_xlim(x_center - 0.5 * new_x_width, x_center + 0.5 * new_x_width)
            self.ax.set_ylim(y_center - 0.5 * new_y_width, y_center + 0.5 * new_y_width)

        # elif self.ax._dragging:
        #     dx = event.x - self.ax._drag_start[0]
        #     dy = event.y - self.ax._drag_start[1]
        #     dx /= -1000
        #     dy /= -1000
        #     xlim = self.ax.get_xlim()
        #     ylim = self.ax.get_ylim()
        #     x_width = xlim[1] - xlim[0]
        #     y_width = ylim[1] - ylim[0]
        #     new_x_center = xlim[0] + x_width / 2 + dx
        #     new_y_center = ylim[0] + y_width / 2 + dy
        #     self.ax.set_xlim(new_x_center - x_width / 2, new_x_center + x_width / 2)
        #     self.ax.set_ylim(new_y_center - y_width / 2, new_y_center + y_width / 2)
            
        plt.draw()
    
    def on_mouse_scroll(self, event):
        if event.button == 'up':
            self.ax._zoom_scale *= 0.9
        elif event.button == 'down':
            self.ax._zoom_scale *= 1.1


class RealTimePlot_3D:
    def __init__(self, ax):
        self.ax = ax
        
        self.ax._button_pressed = False
        self.ax._button_press_event = None
        self.ax._dragging = False
        self.ax._drag_start = (0, 0)
        
        self.ax.view_init(elev=30, azim=30)
        self.ax.dist = 10
    
    def update_plot(self):
        x = np.random.rand(10)
        y = np.random.rand(10)
        z = np.random.rand(10)
        
        self.ax.cla()
        self.ax.scatter(x, y, z)
    
    def on_button_press(self, event):
        if event.button == 1:
            self.ax._button_pressed = True
            self.ax._button_press_event = event
        elif event.button == 3:
            self.ax._dragging = True
            self.ax._drag_start = (event.x, event.y)
    
    def on_button_release(self, event):
        if event.button == 1:
            self.ax._button_pressed = False
        elif event.button == 3:
            self.ax._dragging = False
    
    def on_mouse_move(self, event):
        if self.ax._button_pressed:
            dx = event.x - self.ax._button_press_event.x
            dy = event.y - self.ax._button_press_event.y
            self.ax.view_init(elev=self.ax.elev - dy, azim=self.ax.azim + dx)
        elif self.ax._dragging:
            dx = event.x - self.ax._drag_start[0]
            dy = event.y - self.ax._drag_start[1]
            self.ax._drag_start = (event.x, event.y)
            self.ax.azim -= dx * 0.3
        
        plt.draw()
        

class Serial_Data_Read():
    def __init__(self):
        self.ser = serial.Serial()
        self.read_is_done = False
        self.port_name = None
        self.baud_rate = None
        self.byte_size = 8     #字节大小  8
        self.received_data = {}
        self.received_header = '6A'
        self.received_data_update = False
        self.received_raw_data = []
        
        # self.send_data_structure = {
        #     'header': INT,
        #     'ecd_set': UINT16_T,
        #     'check_sum': INT
        # }
        self.send_data = {}
        self.send_header = 'A6'
        self.send_data_update = False
        self.send_raw_data = []
    
    
    def OpenSerialPort(self):
        if self.port_name != None:
            self.ser.port=self.port_name    #端口，用与电脑相匹配
            self.ser.baudrate=self.baud_rate  #波特率    9600
            self.ser.bytesize=self.byte_size     #字节大小  8
            self.ser.open()
            if(self.ser.isOpen()):
                print("串口打开成功！")
                return True
            else:
                print("串口打开失败！")
                return False
        else:
            print("无可用端口！")
            return False
        
        
    def CloseSerialPort(self):
        self.ser.close()
        if(self.ser.isOpen()):
            print("串口关闭失败！")
            return False
        else:
            print("串口关闭成功！")
            return True
            
            
    def ReadData(self):
        try:
            self.ser.reset_input_buffer()# 清除接收数据的缓冲区
            
            self.received_data_update = False
            received_data = {} #解码数据
            received_raw_data = [] #原始2进制数据
            
            data = self.ser.read()#读取header
            received_data['header'] = (data.hex()).upper()
            
            #检验并在出错时重新读取header
            cnt = 0
            while received_data['header'] != self.received_header.upper() and cnt < 10:#判断是否为起始符
                data = self.ser.read()#读取一个字节的数据
                received_data['header'] = (data.hex()).upper()
                cnt+=1
            
            if received_data.get('header') == self.received_header.upper():# 判断是否为起始符
                received_raw_data.clear()
                received_raw_data.append(data)#添加header数据到原始数据中
                
                data = self.ser.read(2)#读取length
                received_raw_data.append(data)
                received_data['length'] = int.from_bytes(data, byteorder='little')#解码长度
                L = WORD_COUNT + 5#每段数据的长度
                n = (received_data['length'] - 5)//L#计算数据组数
                
                data = self.ser.read(received_data['length'] - 3)#读取剩余数据
                received_raw_data.append(data)
                received_data['check_sum'] = int.from_bytes(data[-2:], byteorder='little')#解码CheckSum
                
                #这里要先varify一下crc防止数据出错
                if self.VarifyCRC(received_raw_data, received_data):#Varify通过之后进行数据解析
                    # print(BinaryToFloat(data[-6:-2]))
                    for i in range(n):#解码每段数据
                        data_segment = data[i*15:(i+1)*15]
                        name = BinaryArrayToName(data_segment[:WORD_COUNT])#获取数据名
                        # print('name =', name)
                        if name == None:
                            continue
                        data_type = data_segment[10]
                        if data_type == UINT32_T:
                            received_data[name] = int.from_bytes(data_segment[11:], byteorder='little')
                        elif data_type == FLOAT:
                            received_data[name] = BinaryToFloat(data_segment[11:])
                    self.received_data = received_data.copy()
                    self.received_data_update = True
                    self.received_raw_data = b''.join(received_raw_data)
                    return READ_SUCCESSFULLY
                else:
                    return READ_CRC_ERROR
            return READ_HEADER_ERROR
        except:
            return READ_FAILED
            
            
    
    def SendData(self):
        # 发送数据，数据格式为：起始符+数据+校验和
        try:
            data_list = [b'\xa6']*5
            wCRC = self.GetCRC_16(data_list)
            data = b''.join(data_list[:-2]) + wCRC.to_bytes(2, byteorder='little')
            self.ser.write(data)
            return SEND_SUCCESSFULLY
        except:
            return SEND_FAILED
    
    
    def VarifyCRC(self,received_raw_data_list,received_data):
        return self.GetCRC_16(received_raw_data_list) == received_data.get('check_sum')
    
    
    def GetCRC_16(self,raw_data_list):
        CRC16_INIT = 0xFFFF
        raw_data = b''.join(raw_data_list)
        wCRC = CRC16_INIT
        for ch_data in raw_data[:-2]:
            wCRC = (wCRC>>8)^W_CRC_TABLE[(wCRC^ch_data)&0x00ff]
        return wCRC
    
    
    def AppendCRC(self):
        pass
    
    
    def PortIsOpen(self):
        return self.ser.isOpen()





if __name__ == '__main__':

    sdr = Serial_Data_Read()
    sdr.port_name = 'COM7'
    sdr.baud_rate = 115200
    sdr.byte_size = 8
    sdr.OpenSerialPort()#打开串口
    n=0
    data_dict_list = []
    while True :
        sdr.SendData()
        sdr.ReadData()
        # print(sdr.ReadData())
        # print(sdr.received_data)
        # data_dict_list.append(sdr.received_data.copy())
        
        break
    
    sdr.CloseSerialPort()#关闭串口

    # fig_2d, ax_2d = plt.subplots(figsize=(15,7.5))
    # plot_2d = RealTimePlot_2D(ax_2d)
    # plot_2d.x = np.linspace(0, 2 * np.pi, 100)
    # plot_2d.y = np.sin(plot_2d.x)+np.random.rand(100)/10
    
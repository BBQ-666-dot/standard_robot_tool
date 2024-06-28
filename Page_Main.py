import tkinter as tk
import tkinter.ttk as ttk

from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process
from OperationTypedef import OPEN_USB, CLOSE_USB
from CustomWidget import PostureGraphModel

class SerialModel(tk.LabelFrame):
    def __init__(self, master, usb:USB_Device, operations:list, **kwargs):
        super().__init__(master, **kwargs)
        self.config(text='串口设置')
        self.operations = operations
        self.usb = usb
        self.AddWidget()
        self.CheckPort()
        self.UpdateSerialPortList()
        return
    
    def AddWidget(self):
        line_height = 30
        label_width = 100
        label_start_x = 10
        opration_start_x = 80
        
        # 第1块：串口设置
        # 第1行：选择串口
        Label_Port = tk.Label(
                        self,
                        text='端口号:',
                        font=('黑体', 12),
                        anchor='w'
                        )
        Label_Port.place(x=label_start_x, y=10, width=label_width, height=line_height)
        
        # 获取可用端口
        available_ports = self.usb.get()
        port_name_list = list(list(zip(*list(map(list,available_ports))))[0]) if len(available_ports) > 0 else ['无可用端口']
        self.combobox_port = ttk.Combobox(
                        self,
                        font=('Arial', 12),
                        values = port_name_list,
                        postcommand = self.UpdateSerialPortList,
                        state='readonly'
                    )
        self.combobox_port.place(x=opration_start_x, y=10, width=100, height=line_height)
        self.combobox_port.current(0)
        
        # 第2行：开关串口
        self.label_toggle_port = tk.Label(
                        self,
                        bg='red'
                    )
        self.label_toggle_port.place(x=label_start_x + 15, y=10+line_height, width=line_height, height=line_height)

        self.button_toggle_Port = tk.Button(
                        self,
                        text='打开端口',
                        font=('黑体', 12),
                        width=10,height=1,
                        command=self.TogglePort
                    )
        self.button_toggle_Port.place(x=opration_start_x, y=10+line_height, width=100, height=line_height)
        return

    ############################################################
    #  实时任务
    #  CheckPort 检测串口状态
    #  UpdateSerialPortList 更新串口列表
    ############################################################
    def CheckPort(self):
        if self.usb.is_open: # 串口已经打开
            self.label_toggle_port['bg'] = 'green'
            self.button_toggle_Port['text'] = '关闭端口'
        else:
            self.label_toggle_port['bg'] = 'red'
            self.button_toggle_Port['text'] = '打开端口'
        
        self.after(50, self.CheckPort)# 50ms后检查串口状态
        return
    
    def UpdateSerialPortList(self):
        '''更新串口列表'''
        available_ports = self.usb.get()
        port_name_list = list(list(zip(*list(map(list,available_ports))))[0] if len(available_ports) > 0 else ['无可用端口'])
        self.combobox_port.configure(values=port_name_list)
        if self.combobox_port.get() not in port_name_list:
            self.combobox_port.current(0)
        
        self.after(50, self.UpdateSerialPortList)# 50ms后更新串口列表
        return

    ############################################################
    #  回调函数
    #  TogglePort 变更串口状态
    ############################################################
    def TogglePort(self):
        if self.label_toggle_port['bg'] == 'red':
            if self.combobox_port.get() == '无可用端口':
                return
            self.usb.modify(self.combobox_port.get(),9600,8,1,"N")
            self.operations.append(OPEN_USB)
            self.label_toggle_port['bg'] = 'green'
            self.button_toggle_Port['text'] = '关闭端口'
        else:
            self.operations.append(CLOSE_USB)
            self.label_toggle_port['bg'] = 'red'
            self.button_toggle_Port['text'] = '打开端口'
        return
        

class Page_Main(tk.Frame):
    def __init__(self, master, usb:USB_Device, data_process:Data_Process, operations:list, **kwargs):
        super().__init__(master, **kwargs)
        self.id = 1
        self.operations = operations
        self.data_process = data_process
        self.usb = usb
        self.after(200, self.UpdateImuPos)# 200ms后更新IMU姿态信息
    
    def CreatePage(self,width:int,height:int):
        '''
        主页包含的内容：
        1. 机器人的姿态信息
        2. 串口的连接状态
        3. 串口的数据接收状态
        4. 串口的开关
        '''
        pass
        # tk.Label(self, text='主页面').pack(pady=(50, 0))
        
        SerialModel(self,
                   usb = self.usb,
                   operations = self.operations
                   ).place(x=10,y=10,width=width*0.3,height=height*0.2)

        # IMU姿态信息
        self.pos_graph_model = PostureGraphModel(self)
        self.pos_graph_model.place(x=20 + width*0.3, y=10, width=250, height=250)
        return
    
    ############################################################
    #  实时任务
    #  UpdateImuPos 更新IMU姿态信息
    ############################################################
    
    def UpdateImuPos(self):
        thetas = {
            "yaw": self.data_process.imu_data.latest['yaw'],
            "pitch": self.data_process.imu_data.latest['pitch'],
            "roll": self.data_process.imu_data.latest['roll']
        }
        self.pos_graph_model.UpdateGraph(thetas)
        self.after(20, self.UpdateImuPos)# 20ms后更新IMU姿态信息
        
        
        
    
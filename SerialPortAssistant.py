import tkinter as tk
import tkinter.ttk
import tkinter.messagebox
from PIL import Image
import serial.tools.list_ports
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sys

import SerialPortAssistant_lib as spl
import Help_Windows as hw
import SPALog as log

#用于判断是添加了数据还是删除了数据
ADD_SENDDATA = 0
DELETE_SENDDATA = 1
MODIFY_SENDDATA = 2
#Show_State 的选项
DECODED_DATA = 0
RAW_DATA_16 = 1
RAW_DATA_2 = 2
#Add_Timestamp 的选项
ADD_TIMESTAMP = 0
NO_TIMESTAMP = 1
#Show_Image 的选项
SHOW_IMAGE = 0
NO_SHOW_IMAGE = 1
#数据储存区的最大长度
MAX_DATA_STORAGE_LENGTH = 5000
#采样点个数变化最小值
MIN_SAMPLES_NUMBER_DELTA = 10

class Const():
    READ_DATA_INTERVAL = 50 #(ms)
    PLOT_TIME_INTERVAL = 100 #(ms)
    MAX_DATA_STORAGE_LENGTH = 5000 #(个)数据储存区的最大长度
    MIN_SAMPLES_NUMBER_DELTA = 100


# data_storage = []
# port_is_open = False
# is_receive_data = False


def BlankFunction():
    '''空函数，用于占位'''
    print('BlankFunction')


class ReceivedDataNameModel(tk.Frame):
    '''接收数据名称列表'''
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.list_Checkbuttons = [] #存储Checkbutton的列表：[(Checkbutton, IntVar),...]，其中IntVar为Checkbutton的状态
        self.name_list = [] #存储数据名称的列表
        self.selected_names = [] #存储被选中的数据名称
        self.name_list_is_updated = False #数据名称列表是否更新

    def AddWidget(self):
        # 创建label提示内容
        self.label = tk.Label(self, text="接收到的数据名称：")
        self.label.pack(side="top", fill="x")
        # 创建一个Canvas和一个Scrollbar
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        # 更改canvas的大小
        self.canvas.config(width=200, height=300)
        # 创建一个Frame来包含所有的Checkbutton
        self.frame = tk.Frame(self.canvas)
        # 将Scrollbar放到Canvas的右边，填充Y方向
        self.scrollbar.pack(side="right", fill="y")
        # 将Canvas放到Scrollbar的左边，填充两个方向
        self.canvas.pack(side="left", fill="both", expand=True)
        # 将Frame放到Canvas中
        self.canvas.create_window((0,0), window=self.frame, anchor='nw')
        # 将Canvas的滚动事件与Scrollbar的set方法绑定
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        # 当Frame的大小改变时，更新Canvas的滚动区域
        self.frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # 绑定鼠标滚轮事件
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # 添加Checkbutton
        for i in range(20):
            self.AddCheckbutton(f"checkbutton{i}")


    def UpdateCheckbuttons(self):
        for i,name in enumerate(self.name_list):
            if i<self.list_Checkbuttons.__len__():
                self.ChangeCheckbutton(name, i)
            else:
                self.AddCheckbutton(name)
        for i in range(self.name_list.__len__(),self.list_Checkbuttons.__len__()):
            self.RemoveCheckbutton(i)


    def AddCheckbutton(self, text:str):
        '''
        添加Checkbutton
        text:Checkbutton的文本
        '''
        var = tk.IntVar()
        var.set(0)
        checkbutton = tk.Checkbutton(self.frame, text=text, variable=var, command=lambda:self.SelectedNamesUpdate(text,var.get()))
        self.list_Checkbuttons.append((checkbutton, var))
        checkbutton.pack()


    def ChangeCheckbutton(self, text:str, index:int):
        '''
        修改Checkbutton的文本
        text:Checkbutton的文本
        index:Checkbutton的索引
        '''
        checkbutton, var = self.list_Checkbuttons[index]
        original_text = checkbutton.cget('text')
        if original_text == text:
            return
        if var.get():
            self.selected_names.remove(original_text)
        var.set(0)
        checkbutton.config(text=text)
        checkbutton.config(command=lambda:self.SelectedNamesUpdate(text,var.get()))


    def RemoveCheckbutton(self, index:int):
        '''
        删除Checkbutton
        index:Checkbutton的索引
        '''
        checkbutton, var = self.list_Checkbuttons[index]
        if var.get():
            self.selected_names.remove(checkbutton.cget('text'))
        self.list_Checkbuttons[index][0].destroy()


    def Clear(self):
        '''
        清空Checkbutton
        '''
        for item in self.list_Checkbuttons:
            item[0].destroy()
        self.list_Checkbuttons.clear()
        self.name_list.clear()


    def SelectedNamesUpdate(self,name:str,select:int):
        '''
        更新被选中的数据名称
        name:数据名称
        '''
        if select and (name not in self.selected_names):
            self.selected_names.append(name)
        elif not select and (name in self.selected_names):
            self.selected_names.remove(name)
        log.LogInfo(log.Info_Index.Custom,f"被选中的数据名称:{self.selected_names}")
        self.CallUpdateNames(self.selected_names)


    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta//120), "units")


    def CallStartUpdatePlotGraph(self, names:list):
        pass


    def CallUpdateNames(self, name_list:list):
        pass


    def UpdateNameListCallback(self, name_list:list):
        self.name_list = name_list.copy()
        self.name_list_is_updated = True
        self.UpdateCheckbuttons()
        log.LogInfo(log.Info_Index.Custom,f"数据名称:{self.name_list}")
        if self.selected_names.__len__() == 0:
            self.list_Checkbuttons[0][0].invoke()
        self.CallStartUpdatePlotGraph(self.selected_names)


    def NotUpdateNameListCallback(self):
        self.name_list_is_updated = False


class WaveFormCanavas(FigureCanvasTkAgg):
    '''波形图画布'''
    def __init__(self, master=None, width=5, height=4, dpi=100):
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('time(s)')
        self.ax.set_ylabel('data')
        self.ax.set_title('Waveform')
        self.x = []
        self.y = []
        self.plot, = self.ax.plot(self.x, self.y)
        self.ax.grid()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-1, 1)
        self.ax.set_autoscale_on(False)
        self.ax.set_xticks(np.linspace(0, 10, 11))
        self.ax.set_yticks(np.linspace(-1, 1, 11))
        self.ax.set_xticklabels(np.linspace(0, 10, 11))
        self.ax.set_yticklabels(np.linspace(-1, 1, 11))
        self.ax.tick_params(labelsize=8)
        self.ax.legend()
        self.ax.grid(True)
        super().__init__(self.fig, master=master)
        self.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def plot(self, x, y):
        self.x.append(x)
        self.y.append(y)
        self.plot.set_data(self.x, self.y)
        self.ax.set_xlim(self.x[0], self.x[-1])
        self.draw()



class PlotGraphModel(tk.Frame):
    '''曲线图绘制模块'''
    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.is_drawing = False
        
        self.fig_2d, self.ax_2d = plt.subplots(figsize=(10,6))#(15,7.5)
        self.plot_2d = spl.RealTimePlot_2D(self.ax_2d)
        self.plot_2d.x_label = 'time(s)'
        self.plot_2d.y_label = 'values'
        
        self.start_time:dt.datetime = dt.datetime.now()
        self.data_storage:list = []
        self.sample_number_tkintvar:tk.IntVar = None
        self.names = [] #数据名称列表

    def AddWidget(self):
        self.canvas = FigureCanvasTkAgg(
                        figure=self.fig_2d, 
                        master=self
                    )
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.UpdateGraph()


    def UpdateNamesCallback(self, names:list):
        self.names = names.copy()


    def StartUpdatePlotGraphCallback(self, names:list):
        self.is_drawing = True
        self.start_time = dt.datetime.now()
        self.names = names.copy()
        self.UpdateGraph()


    def StopUpdatePlotGraphCallback(self):
        self.is_drawing = False


    def SelectPlotData(self) -> list:
        show_namber = self.sample_number_tkintvar.get()
        return self.data_storage[-show_namber:]
        # if self.data_storage.__len__() <= show_namber:#如果数据量没有达到显示数量，则选择全部数据
        #     return self.data_storage[:]
        # else :  #否则选择最新的部分
        #     return self.data_storage[-show_namber:]


    def UpdateGraph(self):
        '''更新图像'''
        if self.is_drawing == False: #如果不接收数据，停止执行
            return
        
        x = np.linspace(0, 2 * np.pi, 1000)
        y0 = np.sin(x)+np.random.rand(1000)/10
        
        # TODO：将选择的图像数据显示在图像上
        show_data_storage = self.SelectPlotData()
        x = [(data_dict.get('time') - self.start_time).total_seconds() for data_dict in show_data_storage]
        y_axis_data = []
        for name in self.names:
            y_axis_data.append([data_dict.get(name) for data_dict in show_data_storage])
        
        self.plot_2d.title = 'Waveform'
        self.plot_2d.UpdatePlot(x,y_axis_data,self.names)
        self.canvas.draw()
        
        try:
            self.master.after(Const.PLOT_TIME_INTERVAL, self.UpdateGraph)
        except:
            print(666)


class SerialPortModel(tk.Frame):
    '''串口模块，主要内容如下：\n
        &emsp;&emsp;1.串口参数设置的UI\n
        \t2.串口的打开/关闭按钮\n
        \t3.串口数据的读取\n
    '''
    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.available_ports = []#可用端口列表
        self.sample_number = tk.IntVar()#采样点个数
        self.sample_number.set(1000)
        self.serial_data_read_module = spl.Serial_Data_Read()#串口数据读取模块
        self.received_header = tk.StringVar()
        self.received_header.set('6A')
        self.start_time = dt.datetime.now()
        
        self.data_storage = []#数据储存区
        self.port_is_open = False
        self.is_receive_data = False


    def AddWidget(self) -> None:
        '''添加组件'''
        Label_Set_Port = tk.Label(
                        self,
                        text='设置端口信息:',
                        font=('黑体', 12),
                        width=24,height=1,
                        anchor='w'
                    )
        Label_Set_Port.pack(side=tk.TOP)

        Frame_Port = tk.Frame(
                        self,
                    )
        Frame_Port.pack(side=tk.TOP)

        Label_Port = tk.Label(
                        Frame_Port,
                        text='端口号:',
                        font=('黑体', 12),
                        width=10,height=1,
                        anchor='w'
                    )
        Label_Port.pack(side=tk.LEFT)

        self.Combobox_Port = tkinter.ttk.Combobox(
                        Frame_Port,
                        width=10,height=1,
                        font=('Arial', 12),
                        values=list(list(zip(*list(map(list,self.available_ports))))[0]) if len(self.available_ports) > 0 else ['无可用端口'],
                        postcommand = self.UpdateSerialPortList,
                        state='readonly'
                    )
        self.Combobox_Port.pack(side=tk.RIGHT)
        self.Combobox_Port.current(0)
        
        Frame_Baud_Rate = tk.Frame(
                        self,
                    )
        Frame_Baud_Rate.pack(side=tk.TOP)

        Label_Baud_Rate = tk.Label(
                        Frame_Baud_Rate,
                        text='波特率:',
                        font=('黑体', 12),
                        width=10,height=1,
                        anchor='w'
                    )
        Label_Baud_Rate.pack(side=tk.LEFT)

        self.Combobox_Baud_Rate = tkinter.ttk.Combobox(
                        Frame_Baud_Rate,
                        width=10,height=1,
                        font=('Arial', 12),
                        values=[9600,115200],
                        state='readonly'
                    )
        self.Combobox_Baud_Rate.pack(side=tk.RIGHT)
        self.Combobox_Baud_Rate.current(1)



        Frame_Samples_Number = tk.Frame(
                        self,
                    )
        Frame_Samples_Number.pack(side=tk.TOP)

        Label_Samples_Number = tk.Label(
                        Frame_Samples_Number,
                        text='采样点个数:',
                        font=('黑体', 12),
                        width=11,height=1,
                        anchor='w'
                    )
        Label_Samples_Number.pack(side=tk.LEFT)

        self.Entry_Samples_Number = tk.Entry(
                        Frame_Samples_Number,
                        width=11,
                        font=('Arial', 12),
                        textvariable=self.sample_number,
                        state='normal'
                    )
        self.Entry_Samples_Number.pack(side=tk.RIGHT)
        self.Entry_Samples_Number.bind('<MouseWheel>',self.Entry_Samples_Number_OnMouseScroll)
                        
        
        Frame_On_Off_Port = tk.Frame(
                        self,
                    )
        Frame_On_Off_Port.pack(side=tk.TOP)

        self.Label_On_Off_Port = tk.Label(
                        Frame_On_Off_Port,
                        width=2,height=1,
                        bg='red'
                    )
        self.Label_On_Off_Port.pack(side=tk.LEFT)

        self.Button_On_Off_Port = tk.Button(
                        Frame_On_Off_Port,
                        text='打开端口',
                        font=('黑体', 12),
                        width=10,height=1,
                        command=self.On_Off_Port_Click
                    )
        self.Button_On_Off_Port.pack(side=tk.RIGHT)


    def Entry_Samples_Number_OnMouseScroll(self,event) -> None:
        '''鼠标滚轮滚动时增减采样点个数'''
        self.sample_number.set(self.sample_number.get()+event.delta//120*Const.MIN_SAMPLES_NUMBER_DELTA)


    def UpdateSerialPortList(self) -> None:
        '''更新串口列表'''
        # 获取可用的串口端口信息
        self.available_ports = serial.tools.list_ports.comports()
        port_name_list = list(list(zip(*list(map(list,self.available_ports))))[0]) if len(self.available_ports) > 0 else ['无可用端口']
        self.Combobox_Port.configure(values=port_name_list)
        if self.Combobox_Port.get() not in port_name_list:
            self.Combobox_Port.current(0)


    def On_Off_Port_Click(self) -> None:
        '''打开/关闭串口'''
        if self.Button_On_Off_Port['text'] == '打开端口':
            #传入参数
            self.data_storage.clear()
            if self.Combobox_Port.get() == '无可用端口':
                self.serial_data_read_module.port_name = None
                log.LogWarning(log.Warning_Index.DoNotFindPort)
            else:
                self.serial_data_read_module.port_name = self.Combobox_Port.get()
            
            self.serial_data_read_module.baud_rate = int(self.Combobox_Baud_Rate.get())
            self.serial_data_read_module.received_header = self.received_header.get()
            #打开串口
            serial_port_is_open = self.serial_data_read_module.OpenSerialPort()
            if serial_port_is_open: #串口打开成功
                log.LogInfo(log.Info_Index.PortIsOpen)
                self.start_time = dt.datetime.now()#设置串口开始打开时间为当前时间
                self.port_is_open = True #设置当前状态为串口打开
                self.Button_On_Off_Port['text'] = '关闭端口' #更改开关状态
                self.Label_On_Off_Port['bg'] = 'green'

                #设置状态
                self.Combobox_Port.configure(state='disabled') #串口打开状态下不能更改串口号
                self.Combobox_Baud_Rate.configure(state='disabled') #串口打开状态下不能更改波特率

                #开始接收数据
                self.is_receive_data = True #设置当前状态为接收数据
                self.Receive_Data() #开始接收数据
                log.LogInfo(log.Info_Index.PortIsReceivingData)
                # self.CallStartUpdatePlotGraph() #开始更新显示图像

            else:
                #在输出的信息框中显示错误信息
                log.LogError(log.Error_Index.PortOpenFailed)
        else:
            serial_port_is_not_open = self.serial_data_read_module.CloseSerialPort()
            if serial_port_is_not_open: #串口关闭成功
                log.LogInfo(log.Info_Index.PortIsClose)
                self.port_is_open = False
                self.is_receive_data = False
                self.Button_On_Off_Port['text'] = '打开端口'
                self.Label_On_Off_Port['bg'] = 'red'
                #设置状态
                self.Combobox_Port.configure(state='readonly')
                self.Combobox_Baud_Rate.configure(state='readonly')
                # self.Text_SendData_Structure.configure(state='normal')
                #更新串口列表
                self.UpdateSerialPortList()
                # #清除储存的数据
                # self.data_storage.clear()
                #停止更新名称列表
                self.CallNotUpdateNameList()
            else:
                #在输出的信息框中显示错误信息
                pass


    def MaintainDataStorageLength(self) -> bool:
        '''维持数据储存区长度，并返回是否达到最长长度'''
        res = False
        while len(self.data_storage) > Const.MAX_DATA_STORAGE_LENGTH:
            self.data_storage.pop(0)
            if not res:
                res = True
        return res


    def Receive_Data(self) -> None:
        '''接收数据'''
        if self.is_receive_data == False:#如果不接收数据，停止执行
            log.LogInfo(log.Info_Index.PortIsNotReceivingData)
            # self.CallStopUpdatePlotGraph()#停止绘图
            return
        #如果超过1000ms秒没有接收到数据，关闭串口
        MAX_STOP_TIME = 1000 #(ms)
        if self.data_storage.__len__() == 0 and dt.datetime.now() - self.start_time > dt.timedelta(milliseconds=MAX_STOP_TIME):
            # 打开串口后一直没有接收到数据，关闭串口
            log.LogWarning(log.Warning_Index.HaveNotReceiveAnyData)
            self.On_Off_Port_Click()
            return
        elif self.data_storage.__len__() > 0 and dt.datetime.now() - self.data_storage[-1].get('time') > dt.timedelta(milliseconds=MAX_STOP_TIME):
            log.LogWarning(log.Warning_Index.HaveNotReceiveAnyData)
            self.On_Off_Port_Click()
            return

        if self.data_storage.__len__() == 1:#如果是第一次接收到数据，更新数据名称列表
            name_list = list(self.data_storage[0].keys())
            name_list.remove('time')
            name_list.remove('header')
            name_list.remove('length')
            name_list.remove('check_sum')
            self.CallUpdateNameList(name_list)
        # log.LogInfo(log.Info_Index.Custom,f"已存储{self.data_storage.__len__()}个数据")

        data_send_state = self.serial_data_read_module.SendData()#发送数据，激活c板发回数据
        data_read_state = self.serial_data_read_module.ReadData()#读取数据
        if data_read_state == spl.READ_FAILED or data_send_state == spl.SEND_FAILED:
            log.LogError(log.Error_Index.PortReadFailed)
            self.On_Off_Port_Click()#如果读取数据失败，关闭串口
        elif data_read_state == spl.READ_SUCCESSFULLY:
            current_time = dt.datetime.now()#获取当前时间
            data_dict = self.serial_data_read_module.received_data.copy()#获取数据字典
            data_dict['time'] = current_time
            self.data_storage.append(data_dict)#添加新数据
            self.MaintainDataStorageLength()
        self.master.after(Const.READ_DATA_INTERVAL, self.Receive_Data)  #调用自身，实现x毫秒的间隔


    def CallUpdateNameList(self, name_list:list):
        pass


    def CallNotUpdateNameList(self):
        pass


    # def CallStartUpdatePlotGraph(self):
    #     pass


    def CallStopUpdatePlotGraph(self):
        pass




class SendDataModel(tk.Frame):
    '''数据发送模块，包含了数据发送的一些设置'''
    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.send_data_list = []#发送数据的列表
        self.send_data_data = tk.StringVar()
        self.send_data_data.set('0')


    def AddWidget(self):
        # Frame_Text_SendData_Structure = tk.Frame(
        #                 Frame_Data_Structure,
        #                 #relief='groove',bd=1
        #             )
        # Frame_Text_SendData_Structure.pack(side=tk.TOP)
        #root/Frame_Right/Frame_SendData_Structure
        Label_SendData_Structure = tk.Label(
                        self,
                        text='发送的数据:',
                        font=('黑体', 12),
                        width=35,height=1,
                        anchor='w'
                    )
        Label_SendData_Structure.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        Frame_SendData_Name = tk.Frame(
                        self,
                    )
        Frame_SendData_Name.pack(side=tk.TOP)
        
        Label_SendData_Name = tk.Label(
                        Frame_SendData_Name,
                        text='数据名称',
                        font=('黑体', 12),
                        width=10,height=1,
                        anchor='w'
                    )
        Label_SendData_Name.pack(side=tk.LEFT)
        
        self.Combobox_SendData_Name = tkinter.ttk.Combobox(
                        Frame_SendData_Name,
                        width=10,height=1,
                        font=('Arial', 12),
                        values=[],
                        state='normal'
                    )
        self.Combobox_SendData_Name.pack(side=tk.RIGHT)
        self.Combobox_SendData_Name.bind("<KeyRelease>", self.Combobox_SendData_Name_OnKeyRelease)
        self.Combobox_SendData_Name.bind("<Control-KeyPress-Delete>", self.Combobox_SendData_Name_OnCtrlDel)
        self.Combobox_SendData_Name.bind("<<ComboboxSelected>>", self.Combobox_SendData_Name_Selected)
        # self.Combobox_SendData_Name.bind("<BackSpace>", self.Combobox_SendData_Name_OnBackSpace)
        # self.Combobox_SendData_Name.bind("<Delete>", self.Combobox_SendData_Name_OnDelete)
        # self.Combobox_SendData_Name.bind("<Return>", self.Combobox_SendData_Name_OnReturn)
        # self.Combobox_SendData_Name.bind("<KeyPress>", self.Combobox_SendData_Name_OnKeyPress)
        
        Frame_SendData_Type = tk.Frame(
                        self,
                    )
        Frame_SendData_Type.pack(side=tk.TOP)
        
        Label_SendData_Type = tk.Label(
                        Frame_SendData_Type,
                        text='数据类型',
                        font=('黑体', 12),
                        width=10,height=1,
                        anchor='w'
                    )
        Label_SendData_Type.pack(side=tk.LEFT)
        
        self.Combobox_SendData_Type = tkinter.ttk.Combobox(
                        Frame_SendData_Type,
                        width=10,height=1,
                        font=('Arial', 12),
                        values=['INT','FLOAT'],
                        state='disabled'#readonly
                    )
        self.Combobox_SendData_Type.pack(side=tk.RIGHT)
        self.Combobox_SendData_Type.current(0)
        self.Combobox_SendData_Type.bind("<<ComboboxSelected>>", self.Combobox_SendData_Type_Selected)
        # self.Combobox_SendData_Type.bind("<Return>", self.Combobox_SendData_Type_OnReturn)
        
        Frame_SendData_Data = tk.Frame(
                        self,
                    )
        Frame_SendData_Data.pack(side=tk.TOP)
        
        Label_SendData_Data = tk.Label(
                        Frame_SendData_Data,
                        text='数据内容',
                        font=('黑体', 12),
                        width=10,height=1,
                        anchor='w'
                    )
        Label_SendData_Data.pack(side=tk.LEFT)
        
        self.Entry_SendData_Data = tk.Entry(
                        Frame_SendData_Data,
                        width=12,
                        font=('Arial', 12),
                        textvariable=self.send_data_data,
                        state='disabled' #normal
                    )
        self.Entry_SendData_Data.pack(side=tk.RIGHT)
        # self.Entry_SendData_Data.bind('<MouseWheel>',self.Entry_Samples_Number_OnMouseScroll)
        self.Entry_SendData_Data.bind("<Return>", self.Entry_SendData_Data_OnReturn)
        
        Frame_Preview_SendData = tk.Frame(
                        self,
                    )
        Frame_Preview_SendData.pack(side=tk.TOP)
        
        Label_Preview_SendData = tk.Label(
                        Frame_Preview_SendData,
                        text='预览发送数据',
                        font=('黑体', 12),
                        width=10,height=1,
                        anchor='w'
                    )
        Label_Preview_SendData.pack(side=tk.TOP, fill=tk.X, expand=True)
        
        Frame_Text_Preview_SendData = tk.Frame(
                        Frame_Preview_SendData,
                    )
        Frame_Text_Preview_SendData.pack(side=tk.TOP)
        
        self.Text_Preview_SendData = tk.Text(
                        Frame_Text_Preview_SendData,
                        width=32,height=6,
                        font=('Arial', 12)
                    )
        self.Text_Preview_SendData.pack(side=tk.LEFT)
        self.Text_Preview_SendData.insert('end','发送数据总量：0\n发送于[--:--:--]\n')
        self.Text_Preview_SendData_Scroll = tk.Scrollbar(Frame_Text_Preview_SendData)
        self.Text_Preview_SendData_Scroll.pack(side=tk.RIGHT,fill=tk.Y)
        # 关联滚动条和文本框
        self.Text_Preview_SendData_Scroll.config(command=self.Text_Preview_SendData.yview)
        self.Text_Preview_SendData.config(yscrollcommand=self.Text_Preview_SendData_Scroll.set)


    def Combobox_SendData_Name_OnCtrlDel(self,event):#用于删除发送数据
        # print(self.Combobox_SendData_Name.current())
        index = self.Combobox_SendData_Name.current()
        self.send_data_list.pop(index)
        if self.send_data_list.__len__() == 0:
            self.Combobox_SendData_Name.configure(values=[])
            self.Combobox_SendData_Name.set('')
            self.Combobox_SendData_Type.configure(state='disabled')
            self.Entry_SendData_Data.configure(state='disabled')
        else:#如果数据列表不为空则跳转到第一个发送数据
            self.Combobox_SendData_Name.configure(values=list(zip(*self.send_data_list))[0])
            self.Combobox_SendData_Name.current(0)
            self.Combobox_SendData_Type.current(self.send_data_list[0][1])
            self.send_data_data.set(str(self.send_data_list[0][2]))
        self.UpdatePreviewSendData(updata_state=DELETE_SENDDATA, delete_index=index)
        print(self.Combobox_SendData_Name.current())
        print(self.send_data_list)
    
        
    def Combobox_SendData_Name_OnKeyRelease(self,event):#用于输入内容及检测是否添加数据
        if event.keysym == "Return":
            # print('press Return')
            if self.Combobox_SendData_Name.get() == '':
                tkinter.messagebox.showwarning(title='提示', message='数据名称不能为空！')
            else:
                if self.Combobox_SendData_Name.current() == -1:#发送数据名称不存在则添加新的发送数据
                    self.Combobox_SendData_Type.configure(state='normal')
                    self.Entry_SendData_Data.configure(state='normal')
                    self.Combobox_SendData_Type.current(0)
                    self.send_data_data.set('0')
                    
                    data_name = self.Combobox_SendData_Name.get()
                    data_type = spl.txt_to_type.get(self.Combobox_SendData_Type.get().lower())
                    data = float(self.send_data_data.get())#先将数据转换成float，如果选择类型为int，再转换成int
                    if data_type == spl.UINT32_T:
                        data = int(data)
                        
                    self.send_data_list.append([data_name, data_type, data])
                    
                    self.Combobox_SendData_Name.configure(values=list(zip(*self.send_data_list))[0])
                    self.UpdatePreviewSendData(updata_state=ADD_SENDDATA)
                else:#如果数据名称存在则跳转到对应的发送数据
                    name_index = self.Combobox_SendData_Name.current()
                    self.Combobox_SendData_Type.current(self.send_data_list[name_index][1])
                    self.send_data_data.set(str(self.send_data_list[name_index][2]))
                    
            print(self.Combobox_SendData_Name.current())
            print(self.send_data_list)
        else:
        # elif '0' < event.keysym < '9' or 'A' < event.keysym < 'z' or event.keysym == "BackSpace" or event.keysym == "Delete":
            if self.Combobox_SendData_Name.current() != -1:#如果数据名称存在则跳转到对应的发送数据
                name_index = self.Combobox_SendData_Name.current()
                self.Combobox_SendData_Type.current(self.send_data_list[name_index][1])
                self.send_data_data.set(str(self.send_data_list[name_index][2]))

    
    def Combobox_SendData_Name_Selected(self,event):
        name_index = self.Combobox_SendData_Name.current()
        self.Combobox_SendData_Type.current(self.send_data_list[name_index][1])
        self.send_data_data.set(str(self.send_data_list[name_index][2]))


    def Combobox_SendData_Type_Selected(self,event):
        index = self.Combobox_SendData_Name.current()
        data_type = spl.txt_to_type.get(self.Combobox_SendData_Type.get().lower())
        # if type(self.send_data_list[index][2]) != self.send_data_list[index][1]:
        data = float(self.send_data_data.get())#先将数据转换成float，如果选择类型为int，再转换成int
        if data_type == spl.UINT32_T:
            data = int(data)
        self.send_data_list[index][1] = data_type
        self.send_data_list[index][2] = data
        self.send_data_data.set(str(self.send_data_list[index][2]))
        self.UpdatePreviewSendData(updata_state=MODIFY_SENDDATA,delete_index=index)
        print(self.Combobox_SendData_Name.current())
        print(self.send_data_list)



    def Entry_SendData_Data_OnReturn(self,event):
        index = self.Combobox_SendData_Name.current()
        data_type = self.send_data_list[index][1]
        data = float(self.send_data_data.get())#先将数据转换成float，如果选择类型为int，再转换成int
        if data_type == spl.UINT32_T:
            data = int(data)
        self.send_data_list[index][2] = data
        self.UpdatePreviewSendData(updata_state=MODIFY_SENDDATA,delete_index=index)
        print(self.Combobox_SendData_Name.current())
        print(self.send_data_list)



    def UpdatePreviewSendData(self, updata_state, delete_index=0):
        '''
        ### 更新预览发送数据\n
        预览的发送数据格式如下：\n
        'name[type] = data'
        '''
        row_offset = 2
        self.Text_Preview_SendData.delete("1.7", "2.0-1c")
        self.Text_Preview_SendData.insert("1.7",str(self.send_data_list.__len__()))
        if updata_state == ADD_SENDDATA:
            data_name = self.send_data_list[-1][0]
            data_type = self.send_data_list[-1][1]
            data = self.send_data_list[-1][2]
            self.Text_Preview_SendData.insert(tk.END,f"{data_name}[{spl.type_to_txt[data_type]}] = {data}\n")
        elif updata_state == DELETE_SENDDATA:
            self.Text_Preview_SendData.delete(f"{delete_index + row_offset + 1}.0", f"{delete_index + row_offset + 2}.0")
        elif updata_state == MODIFY_SENDDATA:
            data_name = self.send_data_list[delete_index][0]
            data_type = self.send_data_list[delete_index][1]
            data = self.send_data_list[delete_index][2]
            self.Text_Preview_SendData.delete(f"{delete_index + row_offset + 1}.0", f"{delete_index + row_offset + 2}.0")
            self.Text_Preview_SendData.insert(f"{delete_index + row_offset + 1}.0",f"{data_name}[{spl.type_to_txt[data_type]}] = {data}\n")



class ReceivedDataModel(tk.Frame):
    '''已接收数据处理模块，处理已接收的数据'''
    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.is_drawing = False


    def AddWidget(self):
        # Frame_Output_Data = tk.Frame(
        #                 Frame_Right,
        #                 #relief='groove',bd=1
        #             )
        # Frame_Output_Data.pack(side=tk.TOP)
        Frame_State_Choose = tk.Frame(
                        self,
                        #relief='groove',bd=1
                    )
        Frame_State_Choose.pack(side=tk.TOP)

        Label_Set_Output_Text = tk.Label(
                        Frame_State_Choose,
                        text='选择输出文本的设置:',
                        font=('黑体', 12),
                        width=30,height=1,
                        anchor='w'
                    )
        Label_Set_Output_Text.pack(side=tk.TOP)

        Frame_State_Choose_Line_1 = tk.Frame(
                        Frame_State_Choose,
                        #relief='groove',bd=1
                    )
        Frame_State_Choose_Line_1.pack(side=tk.TOP)

        self.Combobox_Show_State = tkinter.ttk.Combobox(
                        Frame_State_Choose_Line_1,
                        width=12,height=1,
                        font=('黑体', 12),
                        values=['解码后的数据','原始数据(16)','原始数据(2)'],
                        # state='readonly'
                        state='disabled'
                    )
        self.Combobox_Show_State.bind("<<ComboboxSelected>>", self.Combobox_Show_State_Selected)
        self.Combobox_Show_State.pack(side=tk.LEFT,padx=2)
        self.Combobox_Show_State.current(0)

        self.Combobox_Add_Timestamp = tkinter.ttk.Combobox(
                        Frame_State_Choose_Line_1,
                        width=12,height=1,
                        font=('黑体', 12),
                        values=['添加时间戳','不添加时间戳'],
                        state='readonly'
                    )
        self.Combobox_Add_Timestamp.bind("<<ComboboxSelected>>", self.Combobox_Add_Timestamp_Selected)
        self.Combobox_Add_Timestamp.pack(side=tk.LEFT,padx=2)
        self.Combobox_Add_Timestamp.current(0)

        Frame_Output_Data_Info = tk.Frame(
                        self,
                        #relief='groove',bd=1
                    )
        Frame_Output_Data_Info.pack(side=tk.TOP, fill=tk.X, expand=True)

        Label_Output_Text = tk.Label(
                        Frame_Output_Data_Info,
                        text='输出数据:',
                        font=('黑体', 12),
                        width=30,height=1,
                        anchor='w'
                    )
        Label_Output_Text.pack(side=tk.LEFT)


        Frame_Output_Text = tk.Frame(
                        self,
                        #relief='groove',bd=1
                    )
        Frame_Output_Text.pack(side=tk.TOP)

        self.Text_Output_Data = tk.Text(
                        Frame_Output_Text,
                        width=32,height=8,
                        font=('Arial', 12)
                    )
        self.Text_Output_Data.pack(side=tk.LEFT)
        self.Text_Output_Data_Scroll = tk.Scrollbar(Frame_Output_Text)
        self.Text_Output_Data_Scroll.pack(side=tk.RIGHT,fill=tk.Y)
        # 关联滚动条和文本框
        self.Text_Output_Data_Scroll.config(command=self.Text_Output_Data.yview)
        self.Text_Output_Data.config(yscrollcommand=self.Text_Output_Data_Scroll.set)


    def Combobox_Show_State_Selected(self, event):
        '''选择输出文本的设置'''
        self.show_state = self.Combobox_Show_State.current()


    def Combobox_Add_Timestamp_Selected(self, event):
        '''选择是否添加时间戳'''
        self.add_timestamp = self.Combobox_Add_Timestamp.current()

    def UpdateReceivedDataPreviewCallback(self) -> None:
        pass







class SerialPortAssistant():
    """
串口助手APP的主类\n
函数包括：\n
    空函数：\n
        BlankFunction(): 空函数，用于占位\n
    初始化内容：\n
        __init__(): 初始化\n
        InitMenu(): 初始化菜单栏\n
        InitUI(): 初始化UI\n
        InitFrame(): 初始化UI内部组件\n
    监控数据变化：\n
        MonitoringReceviedHeaderVariableChanges(): 监控接收数据帧头变量的变化\n
        MonitoringSampleNumberVariableChanges(): 监控数据采样点个数变量的变化\n
        MaintainDataStorageLength(): 维持数据储存区长度\n
    更新内容：\n
        UpdateGraph(): 更新图像\n
        UpdateSerialPortList(): 更新串口列表\n
    组件绑定的函数：\n
        SaveInputWaveform_Click(): 保存输入波形的按钮函数\n
        Entry_Samples_Number_OnMouseScroll(): 鼠标滚轮滚动时增减采样点个数\n
        Button_Clear_Output_Text_Click(): 清空输出文本框\n
        Combobox_Add_Timestamp_Selected(): 选择是否添加时间戳\n
        Combobox_Show_State_Selected(): 选择显示状态\n
        On_Off_Port(): 打开/关闭串口\n
    功能实现函数：\n
        Receive_Data(): 接收数据\n
        TextToDict(): 将数据据结构的文本转换为字典类型\n
        SaveWaveform(): 保存波形\n
    运行相关：\n
        RunApp(): 运行APP\n
        Quit_App(): 退出APP\n
    """
    
    def __init__(self) -> None:
        '''初始化'''
        self.root = tk.Tk()
        log.LogInfo(log.Info_Index.Custom, '窗口已创建')
        self.serial_data_read_module = spl.Serial_Data_Read()
        self.version = 'V1.6.0'
        log.LogInfo(log.Info_Index.Custom, '版本已确认：' + self.version)
        self.available_ports = serial.tools.list_ports.comports()
        self.show_state = DECODED_DATA
        self.add_timestamp = ADD_TIMESTAMP
        is_receive_data = False
        data_storage = []
        self.show_image = SHOW_IMAGE
        self.start_time = None
        self.plot_time_interval = 30#(ms)图像更新间隔
        self.read_data_interval = 1#(ms)数据读取间隔
        self.received_header = tk.StringVar()
        self.received_header.set('6A')
        self.received_header.trace('w', self.MonitoringReceviedHeaderVariableChanges)
        
        self.send_data_data = tk.StringVar()
        self.send_data_data.set('0')
        self.send_data_list = []#发送数据的列表
        
        self.sample_number = tk.IntVar()
        self.sample_number.set(MAX_DATA_STORAGE_LENGTH)
        self.sample_number.trace('w', self.MonitoringSampleNumberVariableChanges)
        port_is_open = False
        
        self.figure_state = 2#绘多少维的图
        self.fig_3d = plt.figure()
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')

        # self.fig_2d = plt.figure()
        # self.ax_2d = self.fig_2d.add_subplot(111)

        self.fig_2d, self.ax_2d = plt.subplots(figsize=(10,6))#(15,7.5)
        self.plot_2d = spl.RealTimePlot_2D(self.ax_2d)
        self.plot_2d.x_label = 'time(s)'

    
    def InitUI(self):
        '''初始化UI'''
        self.root.title('Serial Port Assistant  ' + self.version)
        self.root.geometry('1450x650')
        self.root.resizable(0,0)
        
        self.InitMenu()
        self.InitFrame()
        self.InitParameter()
        
    def InitParameter(self):
        '''初始化参数'''
        # self.UpdateSerialPortList()
    
    
    def MonitoringReceviedHeaderVariableChanges(self,*args):
        '''监控接收数据帧头变量的变化'''
        if self.received_header.get() == '':
            self.received_header.set('5A')
    
    
    def MonitoringSampleNumberVariableChanges(self,*args):
        '''监控数据采样点个数变量的变化'''
        try:
            if self.sample_number.get() < MIN_SAMPLES_NUMBER_DELTA:
                self.sample_number.set(MIN_SAMPLES_NUMBER_DELTA)
        except:
            self.sample_number.set(MIN_SAMPLES_NUMBER_DELTA)
        
    
    def BlankFunction(self):
        '''空函数，用于占位'''
        pass
    
    
    def SaveReceivedDatas(self):
        # TODO：添加保存数据的功能
        pass
    
    
    def SaveWaveform(self,graph:np.ndarray):
        '''保存波形'''
        # 将NumPy数组转换为PIL图像对象
        pil_image = Image.fromarray(graph)
        
        current_time = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        # 保存图像到磁盘
        spl.mkdir(spl.App_path()+"/Waveform")
        pil_image.save(spl.App_path()+f"/Waveform/{current_time}_{self.Combobox_Output_Data_Label.get()}.png")  # 保存为PNG格式
        
    
    def InitMenu(self):
        '''初始化菜单栏'''
        #菜单栏
        MenuBar = tk.Menu(self.root)
        self.root.config(menu=MenuBar)
        #菜单栏/文件
        Menu_File = tk.Menu(MenuBar, tearoff=0)
        MenuBar.add_cascade(label='文件', menu=Menu_File)
        #菜单栏/文件/打开
        # Menu_File.add_command(label='打开', command=self.BlankFunction)
        #菜单栏/文件/保存
        Menu_File.add_command(label='保存输入波形图', command=self.SaveInputWaveform_Click)
        #菜单栏/文件/退出
        Menu_File.add_command(label='退出', command=self.Quit_App)
        #菜单栏/帮助
        Menu_Help = tk.Menu(MenuBar, tearoff=0)
        MenuBar.add_cascade(label='帮助', menu=Menu_Help)
        #菜单栏/帮助/如何使用
        Menu_Help.add_command(label='如何使用', command=hw.RunHowToUse)
        #菜单栏/帮助/关于
        Menu_Help.add_command(label='关于程序', command=hw.RunAbout)
        #菜单栏/帮助/历史版本
        Menu_Help.add_command(label='历史版本', command=self.BlankFunction)
        #菜单栏/打赏
        MenuBar.add_command(label='打赏', command=hw.RunPay)
    
    
    def SaveInputWaveform_Click(self):
        '''保存输入波形图'''
        if self.figure_state == 2:
            Image = np.frombuffer(self.fig_2d.canvas.tostring_rgb(), dtype=np.uint8)
            Image = Image.reshape(self.fig_2d.canvas.get_width_height()[::-1] + (3,))
        
        self.SaveWaveform(Image)
    
        
    def InitFrame(self):
        '''初始化内部组件'''
        # TODO：添加显示所有接受到的数据名称的列表
        #root
        Frame_Plot = tk.Frame(
                        self.root,
                        #relief='groove',bd=1
                    )
        Frame_Plot.pack(side=tk.LEFT)
        #root/Frame_Plot
        # Frame_Plot_Param = tk.Frame(
        #                 Frame_Plot,
        #                 #relief='groove',bd=1
        #             )
        # Frame_Plot_Param.pack(side=tk.LEFT)
        # #root/Frame_Plot/Frame_Plot_Param
        # Label_Set_Output_Data_Label = tk.Label(
        #                 Frame_Plot_Param,
        #                 text='设置输出数据标签:',
        #                 font=('黑体', 15),
        #                 width=17,height=1,
        #                 anchor='w'
        #             )
        # Label_Set_Output_Data_Label.pack(side=tk.TOP)
        # #root/Frame_Plot/Frame_Plot_Param
        # self.Combobox_Output_Data_Label = tkinter.ttk.Combobox(
        #                 Frame_Plot_Param,
        #                 width=12,
        #                 font=('黑体', 15),
        #                 values=['无数据'],
        #                 postcommand=self.BlankFunction,
        #                 state='readonly'
        #             )
        # self.Combobox_Output_Data_Label.pack(side=tk.TOP)
        # self.Combobox_Output_Data_Label.current(0)
        
        self.received_data_name_moodel = ReceivedDataNameModel(Frame_Plot)
        self.received_data_name_moodel.AddWidget()
        self.received_data_name_moodel.pack(side=tk.LEFT)
        
        
        #图像绘制模块
        self.plot_graph_model = PlotGraphModel(Frame_Plot)
        self.plot_graph_model.AddWidget()
        self.plot_graph_model.pack(side=tk.RIGHT)
        

        #root
        Frame_Right = tk.Frame(
                        self.root,
                        #relief='groove',bd=1
                    )
        Frame_Right.pack(side=tk.RIGHT)
        
        #串口设置模块
        self.serial_port_model = SerialPortModel(Frame_Right)
        self.serial_port_model.AddWidget()
        self.serial_port_model.pack(side=tk.TOP)


        #数据发送模块
        self.send_data_model = SendDataModel(Frame_Right)
        self.send_data_model.AddWidget()
        self.send_data_model.pack(side=tk.TOP)
        
        
        #数据接收模块
        self.received_data_model = ReceivedDataModel(Frame_Right)
        self.received_data_model.AddWidget()
        self.received_data_model.pack(side=tk.TOP)
        

        #将回调函数建立连接
        # self.serial_port_model.CallStartUpdatePlotGraph = self.plot_graph_model.StartUpdatePlotGraphCallback
        self.received_data_name_moodel.CallStartUpdatePlotGraph = self.plot_graph_model.StartUpdatePlotGraphCallback
        self.received_data_name_moodel.CallUpdateNames = self.plot_graph_model.UpdateNamesCallback
        self.serial_port_model.CallStopUpdatePlotGraph = self.plot_graph_model.StopUpdatePlotGraphCallback
        self.serial_port_model.CallUpdateNameList = self.received_data_name_moodel.UpdateNameListCallback
        self.serial_port_model.CallNotUpdateNameList = self.received_data_name_moodel.NotUpdateNameListCallback

        #相关变量建立连接
        self.plot_graph_model.data_storage = self.serial_port_model.data_storage
        self.plot_graph_model.sample_number_tkintvar = self.serial_port_model.sample_number




    # def Combobox_SendData_Type_Selected(self,event):
    #     index = self.Combobox_SendData_Name.current()
    #     data_type = spl.txt_to_type.get(self.Combobox_SendData_Type.get().lower())
    #     # if type(self.send_data_list[index][2]) != self.send_data_list[index][1]:
    #     data = float(self.send_data_data.get())#先将数据转换成float，如果选择类型为int，再转换成int
    #     if data_type == spl.UINT32_T:
    #         data = int(data)
    #     self.send_data_list[index][1] = data_type
    #     self.send_data_list[index][2] = data
    #     self.send_data_data.set(str(self.send_data_list[index][2]))
    #     self.UpdatePreviewSendData(updata_state=MODIFY_SENDDATA,delete_index=index)
    #     print(self.Combobox_SendData_Name.current())
    #     print(self.send_data_list)
    
    
    # def Entry_SendData_Data_OnReturn(self,event):
    #     index = self.Combobox_SendData_Name.current()
    #     data_type = self.send_data_list[index][1]
    #     data = float(self.send_data_data.get())#先将数据转换成float，如果选择类型为int，再转换成int
    #     if data_type == spl.UINT32_T:
    #         data = int(data)
    #     self.send_data_list[index][2] = data
    #     self.UpdatePreviewSendData(updata_state=MODIFY_SENDDATA,delete_index=index)
    #     print(self.Combobox_SendData_Name.current())
    #     print(self.send_data_list)

    
    # def Combobox_SendData_Name_OnCtrlDel(self,event):#用于删除发送数据
    #     # print(self.Combobox_SendData_Name.current())
    #     index = self.Combobox_SendData_Name.current()
    #     self.send_data_list.pop(index)
    #     if self.send_data_list.__len__() == 0:
    #         self.Combobox_SendData_Name.configure(values=[])
    #         self.Combobox_SendData_Name.set('')
    #         self.Combobox_SendData_Type.configure(state='disabled')
    #         self.Entry_SendData_Data.configure(state='disabled')
    #     else:#如果数据列表不为空则跳转到第一个发送数据
    #         self.Combobox_SendData_Name.configure(values=list(zip(*self.send_data_list))[0])
    #         self.Combobox_SendData_Name.current(0)
    #         self.Combobox_SendData_Type.current(self.send_data_list[0][1])
    #         self.send_data_data.set(str(self.send_data_list[0][2]))
    #     self.UpdatePreviewSendData(updata_state=DELETE_SENDDATA, delete_index=index)
    #     print(self.Combobox_SendData_Name.current())
    #     print(self.send_data_list)
    
        
    # def Combobox_SendData_Name_OnKeyRelease(self,event):#用于输入内容及检测是否添加数据
    #     if event.keysym == "Return":
    #         # print('press Return')
    #         if self.Combobox_SendData_Name.get() == '':
    #             tkinter.messagebox.showwarning(title='提示', message='数据名称不能为空！')
    #             # else:#如果数据名称为空则删除对应的发送数据
    #             #     index = self.Combobox_SendData_Name.current()
    #             #     self.send_data_list.pop(index)
    #             #     self.Combobox_SendData_Name.configure(values=list(zip(*self.send_data_list))[0])
    #             #     if self.send_data_list.__len__() == 0:
    #             #         self.Combobox_SendData_Type.configure(state='disabled')
    #             #         self.Entry_SendData_Data.configure(state='disabled')
    #             #     else:#如果数据列表不为空则跳转到第一个发送数据
    #             #         self.Combobox_SendData_Name.current(0)
    #             #         self.Combobox_SendData_Type.current(self.send_data_list[0][1])
    #             #         self.send_data_data.set(str(self.send_data_list[0][2]))
    #         else:
    #             if self.Combobox_SendData_Name.current() == -1:#发送数据名称不存在则添加新的发送数据
    #                 self.Combobox_SendData_Type.configure(state='normal')
    #                 self.Entry_SendData_Data.configure(state='normal')
    #                 self.Combobox_SendData_Type.current(0)
    #                 self.send_data_data.set('0')
                    
    #                 data_name = self.Combobox_SendData_Name.get()
    #                 data_type = spl.txt_to_type.get(self.Combobox_SendData_Type.get().lower())
    #                 data = float(self.send_data_data.get())#先将数据转换成float，如果选择类型为int，再转换成int
    #                 if data_type == spl.UINT32_T:
    #                     data = int(data)
                        
    #                 self.send_data_list.append([data_name, data_type, data])
                    
    #                 self.Combobox_SendData_Name.configure(values=list(zip(*self.send_data_list))[0])
    #                 self.UpdatePreviewSendData(updata_state=ADD_SENDDATA)
    #             else:#如果数据名称存在则跳转到对应的发送数据
    #                 name_index = self.Combobox_SendData_Name.current()
    #                 self.Combobox_SendData_Type.current(self.send_data_list[name_index][1])
    #                 self.send_data_data.set(str(self.send_data_list[name_index][2]))
                    
    #         print(self.Combobox_SendData_Name.current())
    #         print(self.send_data_list)
    #     else:
    #     # elif '0' < event.keysym < '9' or 'A' < event.keysym < 'z' or event.keysym == "BackSpace" or event.keysym == "Delete":
    #         if self.Combobox_SendData_Name.current() != -1:#如果数据名称存在则跳转到对应的发送数据
    #             name_index = self.Combobox_SendData_Name.current()
    #             self.Combobox_SendData_Type.current(self.send_data_list[name_index][1])
    #             self.send_data_data.set(str(self.send_data_list[name_index][2]))

    
    # def Combobox_SendData_Name_Selected(self,event):
    #     name_index = self.Combobox_SendData_Name.current()
    #     self.Combobox_SendData_Type.current(self.send_data_list[name_index][1])
    #     self.send_data_data.set(str(self.send_data_list[name_index][2]))
    

    # def UpdatePreviewSendData(self, updata_state, delete_index=0):
    #     '''
    #     ### 更新预览发送数据\n
    #     预览的发送数据格式如下：\n
    #     'name[type] = data'
    #     '''
    #     row_offset = 2
    #     self.Text_Preview_SendData.delete("1.7", "2.0-1c")
    #     self.Text_Preview_SendData.insert("1.7",str(self.send_data_list.__len__()))
    #     if updata_state == ADD_SENDDATA:
    #         data_name = self.send_data_list[-1][0]
    #         data_type = self.send_data_list[-1][1]
    #         data = self.send_data_list[-1][2]
    #         self.Text_Preview_SendData.insert(tk.END,f"{data_name}[{spl.type_to_txt[data_type]}] = {data}\n")
    #     elif updata_state == DELETE_SENDDATA:
    #         self.Text_Preview_SendData.delete(f"{delete_index + row_offset + 1}.0", f"{delete_index + row_offset + 2}.0")
    #     elif updata_state == MODIFY_SENDDATA:
    #         data_name = self.send_data_list[delete_index][0]
    #         data_type = self.send_data_list[delete_index][1]
    #         data = self.send_data_list[delete_index][2]
    #         self.Text_Preview_SendData.delete(f"{delete_index + row_offset + 1}.0", f"{delete_index + row_offset + 2}.0")
    #         self.Text_Preview_SendData.insert(f"{delete_index + row_offset + 1}.0",f"{data_name}[{spl.type_to_txt[data_type]}] = {data}\n")
                
    
    def Entry_Samples_Number_OnMouseScroll(self,event):
        '''鼠标滚轮滚动时增减采样点个数'''
        self.sample_number.set(self.sample_number.get()+event.delta//120*MIN_SAMPLES_NUMBER_DELTA)
        # if self.sample_number.get() < MIN_SAMPLES_NUMBER_DELTA:
        #     self.sample_number.set(MIN_SAMPLES_NUMBER_DELTA)
    
    # def Button_Clear_Output_Text_Click(self):
    #     '''清空输出文本框'''
    #     self.Text_Output_Data.delete('1.0','end') 
        
        
    # def Combobox_Add_Timestamp_Selected(self, event):
    #     '''选择是否添加时间戳'''
    #     self.add_timestamp = self.Combobox_Add_Timestamp.current()
    
    
    # def Combobox_Show_State_Selected(self, event):
    #     '''选择输出文本的设置'''
    #     self.show_state = self.Combobox_Show_State.current()
        


    def TextToDict(self, struct_text:str):
        '''将数据据结构的文本转换为字典类型'''
        data_struct = struct_text.split('\n')
        data_struct_dict = {}
        data_struct_dict['header'] = spl.UINT8_T
        for data_struct_item in data_struct:
            if data_struct_item == '':
                continue
            if len(data_struct_item.split()) != 2:
                #弹出一个提示框，内容是显示输入的数据结构有误
                tkinter.messagebox.showerror(title='提示', message='输入的数据结构有误！')
            
            data_type = spl.txt_to_type.get(data_struct_item.split()[0].lower(),spl.UINT8_T) 
            data_name = data_struct_item.split()[1]
            data_struct_dict[data_name] = data_type
        data_struct_dict['check_sum'] = spl.INT
        return data_struct_dict


    def UpdateDataLabels(self):
        labels = list(data_storage[0].keys())
        labels.remove('time')
        labels.remove('header')
        labels.remove('length')
        labels.remove('check_sum')
        self.Combobox_Output_Data_Label.configure(values=labels)
        if self.Combobox_Output_Data_Label.get() not in labels:
            self.Combobox_Output_Data_Label.current(0)
        
        
    def RunApp(self):
        '''运行程序'''
        self.root.mainloop()
        
        
    def Quit_App(self):
        '''弹出一个弹窗，询问是否退出，如果是则退出，否则不退出'''
        quit_app = tkinter.messagebox.askyesno(title='提示', message='是否退出？')
        if quit_app:#退出程序
            if port_is_open:
                self.serial_data_read_module.CloseSerialPort()
            sys.exit(0)
        




spa = SerialPortAssistant()
spa.InitUI()
log.LogInfo(log.Info_Index.Custom, '界面初始化完成')
log.LogInfo(log.Info_Index.Custom, '程序运行中...')
spa.RunApp()
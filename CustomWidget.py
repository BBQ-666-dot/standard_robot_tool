
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from lib.matplotlib_for_tk import RealTimePlot_2D, RealTimeGraph_3D
from lib.log_info import LogError , LogInfo , LogWarning


# 旋转矩阵（绕X轴旋转theta角度）
def rotate_x(points, theta):
    rotation_matrix = np.array([[1, 0, 0],
                                [0, np.cos(theta), np.sin(theta)],
                                [0, -np.sin(theta),  np.cos(theta)]])
    return np.dot(points, rotation_matrix)

# 旋转矩阵（绕Y轴旋转theta角度）
def rotate_y(points, theta):
    rotation_matrix = np.array([[np.cos(theta), 0, -np.sin(theta)],
                                [0, 1, 0],
                                [np.sin(theta), 0, np.cos(theta)]])
    return np.dot(points, rotation_matrix)

# 旋转矩阵（绕Z轴旋转theta角度）
def rotate_z(points, theta):
    rotation_matrix = np.array([[np.cos(theta), np.sin(theta), 0],
                                [-np.sin(theta),  np.cos(theta), 0],
                                [0, 0, 1]])
    return np.dot(points, rotation_matrix)

class PlotGraphModel(tk.Frame):
    '''曲线图绘制模块'''
    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.fig_2d, self.ax_2d = plt.subplots(figsize=(10,6))#(15,7.5)
        self.plot_2d = RealTimePlot_2D(self.ax_2d)
        self.plot_2d.x_label = 'time(s)'
        self.plot_2d.y_label = 'values'
        self.plot_2d.title = 'Waveform'
        
        self.AddWidget()
        return

    def AddWidget(self):
        self.canvas = FigureCanvasTkAgg(
                        figure=self.fig_2d, 
                        master=self
                    )
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.UpdateGraph([],[[]],[])
        return
    
    ############################################################
    #  主要功能
    #  UpdateGraph 更新图像
    ############################################################
    def UpdateGraph(self,x_axis_data:list,y_axis_data:list,y_labels:list) -> None:
        '''
        更新图像
        x_axis_data: x轴数据
        y_axis_data: y轴数据列表([y1,y2,y3,...]),包含多个曲线图y轴数据，每个y代表一个曲线图的y轴数据
        y_labels: 每个曲线图的名称列表，数量和y_axis_data一致
        '''
        if len(y_labels) == 0:#如果没有数据名称，绘制空图像
            x=[]
            y_axis_data=[[]]
            self.plot_2d.UpdatePlot(x,y_axis_data,["empty"])
            self.canvas.draw()
        else:
            self.plot_2d.UpdatePlot(x_axis_data,y_axis_data,y_labels)
            self.canvas.draw()
        return

class PostureGraphModel(tk.Frame):
    '''姿态图绘制模块'''
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.fig_3d = plt.figure(figsize=(10,6))#(15,7.5)
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self.graph_3d = RealTimeGraph_3D(self.ax_3d)
        self.AddWidget()
        return

    def AddWidget(self):
        self.canvas = FigureCanvasTkAgg(
                        figure=self.fig_3d, 
                        master=self
                    )
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.UpdateGraph({"roll":0,"pitch":0,"yaw":0})
        return
    
    ############################################################
    #  主要功能
    #  UpdateGraph 更新图像
    ############################################################
    def UpdateGraph(self,thetas:dict) -> None:
        '''
        更新图像
        thetas: 旋转角度列表 roll pitch yaw
        '''
        
        theta_x = thetas['roll']# 绕X轴旋转theta角度
        theta_y = thetas['pitch']
        theta_z = thetas['yaw']
        
        # 原始箭头方向向量
        arrow_x = np.array([1, 0, 0])
        arrow_y = np.array([0, 1, 0])
        arrow_z = np.array([0, 0, 1])
        
        # 旋转箭头方向向量
        rotated_arrow_x = rotate_x(arrow_x, theta_x)
        rotated_arrow_x = rotate_y(rotated_arrow_x, theta_y)
        rotated_arrow_x = rotate_z(rotated_arrow_x, theta_z)

        rotated_arrow_y = rotate_x(arrow_y, theta_x)
        rotated_arrow_y = rotate_y(rotated_arrow_y, theta_y)
        rotated_arrow_y = rotate_z(rotated_arrow_y, theta_z)

        rotated_arrow_z = rotate_x(arrow_z, theta_x)
        rotated_arrow_z = rotate_y(rotated_arrow_z, theta_y)
        rotated_arrow_z = rotate_z(rotated_arrow_z, theta_z)
        
        ax_rotate = {
            "x":rotated_arrow_x,
            "y":rotated_arrow_y,
            "z":rotated_arrow_z
        }
        
        self.graph_3d.UpdatePlot(ax_rotate)
        self.canvas.draw()
        return

class DataNameModel(tk.Frame):
    '''数据名称列表'''
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.list_Checkbuttons = [] #存储Checkbutton的列表：[(Checkbutton, IntVar),...]，其中IntVar为Checkbutton的状态
        self.name_list = [] #存储数据名称的列表
        self.selected_names = [] #存储被选中的数据名称
        self.name_list_is_updated = False #数据名称列表是否更新
        self.AddWidget()

    def AddWidget(self):
        # 创建label提示内容
        self.label = tk.Label(self, text="接收到的数据名称：", font=('黑体', 12))
        self.label.pack(side="top", fill="x")
        # 创建一个Canvas和一个Scrollbar
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        # 更改canvas的大小
        self.canvas.config(width=120, height=100)
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
        # for i in range(20):
        #     self.AddCheckbutton(f"checkbutton{i}")

    def UpdateDataNameList(self, name_list:list):
        '''
        更新数据名称列表
        name_list:数据名称列表
        '''
        self.name_list = name_list.copy()

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
        checkbutton = tk.Checkbutton(self.frame, text=text, variable=var, font=('黑体', 12), command=lambda:self.SelectedNamesUpdate(text,var.get()))
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
        if self.selected_names.__len__() == 0:#如果没有被选中的数据名称，则默认选中第一个数据名称
            self.list_Checkbuttons[0][0].invoke()
        self.CallStartUpdatePlotGraph(self.selected_names)
        LogInfo(f"更新数据名称列表：{self.name_list}")


    def NotUpdateNameListCallback(self):
        self.name_list_is_updated = False

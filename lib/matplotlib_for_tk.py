import serial
import struct
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.axes as maxes
# plt.rcParams['font.family'] = ['SimHei']  # replace with your installed Chinese font
import numpy as np
import os
import sys


class RealTimePlot_2D():
    def __init__(self, ax:maxes.Axes):
        self.ax = ax
        self.title = ''
        self.x_label = ''
        self.y_label = ''

    def UpdatePlot(self,x_axis_data:list,y_axis_data:list,y_labels:list) -> None:
        '''
        绘制图像函数:
        x_axis_data: x轴数据
        y_axis_data: y轴数据列表([y1,y2,y3,...]),包含多个曲线图y轴数据，每个y代表一个曲线图的y轴数据
        y_labels: 每个曲线图的名称列表，数量和y_axis_data一致
        '''
        self.ax.cla()
        for i,y in enumerate(y_axis_data):
            self.ax.plot(x_axis_data, y, label=y_labels[i])
        
        self.ax.set_title(self.title, fontsize=15)  # 添加标题
        self.ax.set_xlabel(self.x_label, fontsize=15)  # 添加X轴标签
        self.ax.set_ylabel(self.y_label, fontsize=15)  # 添加Y轴标签
        self.ax.legend(loc='upper right')  # 添加图例
        self.ax.grid(True)  # 添加网格线
        return None



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
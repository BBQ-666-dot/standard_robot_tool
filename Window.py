'''
上位机窗口
'''

import tkinter as tk
import tkinter.ttk
import tkinter.messagebox
from tkinter import font

from PIL import Image
import serial.tools.list_ports
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sys

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process

from Page_Main import Page_Main
from Page_Debug import Page_Debug
from Page_RobotState import Page_Robot_State

class Window():
    def __init__(self, usb:USB_Device, data_process:Data_Process, operations:list) -> None:
        self.usb = usb
        self.data_process = data_process
        self.operations = operations
        
        self.window = tk.Tk()
        LogInfo("窗口已创建")
        self.version = 'V1.0.0'
        LogInfo('版本已确认：' + self.version)
        self.height = 0
        self.width = 0
        
        self.page_main = Page_Main(self.window)
        self.page_debug = Page_Debug(self.window)
        self.page_robot_state = Page_Robot_State(self.window)
    
    def BlankFunction(self):
        '''空函数，用于占位'''
        pass
############################################################
#  主要功能
#  InitApp 初始化程序
#  RunApp 运行程序
#  QuitApp 退出程序
############################################################
    def InitApp(self, width:int, height:int):
        '''初始化程序'''
        self.height = height
        self.width = width
        self.InitUI()
        LogInfo('UI已初始化')
    
    def RunApp(self):
        '''运行程序'''
        self.window.mainloop()
    
    # def QuitApp(self):
    #     '''弹出一个弹窗，询问是否退出，如果是则退出，否则不退出'''
    #     pass
    #     quit_app = tkinter.messagebox.askyesno(title='提示', message='是否退出？')
    #     if quit_app:#退出程序
    #         if self.serial_port_model.port_is_open:
    #             self.serial_data_read_module.CloseSerialPort()
    #         sys.exit(0)

############################################################
#  切换界面
#  SwitchPage 切换界面
############################################################
    
    def SwitchPage(self, page_id:int):
        if page_id == self.page_main.id:
            return
            self.page_main.lift()
        elif page_id == self.page_debug.id:
            return
            self.page_debug.lift()
        elif page_id == self.page_robot_state.id:
            return
            self.page_robot_state.lift()


############################################################
#  界面创建
#  InitUI 初始化UI
#  CreateMenu 创建菜单栏
############################################################
    
    def InitUI(self):
        '''初始化UI'''
        self.window.title('StandardRobot++ Tool  ' + self.version)
        self.window.geometry(f'{self.width}x{self.height}')
        self.window.resizable(0,0)
        self.CreateMenu()

    def CreateMenu(self):
        '''创建菜单栏'''
        button_width = 100
        button_height = 50
        
        button_width = self.width / 3
        button_height = 30
        
        button_font = ('黑体', 15)
        
        # def on_enter(e):
        #     e.widget.config(background='darkgrey')
        # def on_leave(e):
        #     e.widget.config(background='SystemButtonFace')  # 使用系统默认按钮背景色
        
        button_main = tk.Button(self.window, 
                                text='主界面', 
                                relief=tk.FLAT,
                                command=lambda:self.SwitchPage(self.page_main.id),
                                font=button_font)
        button_main.place(x=button_width * 0, y=0, width=button_width, height=button_height)
        # button_main.bind("<Enter>", on_enter)
        # button_main.bind("<Leave>", on_leave)
        
        button_debug = tk.Button(self.window, 
                                text='调试数据', 
                                relief=tk.FLAT,
                                command=lambda:self.SwitchPage(self.page_main.id),
                                font=button_font)
        button_debug.place(x=button_width * 1, y=0, width=button_width, height=button_height)

        button_robot_state = tk.Button(self.window, 
                                text='机体状态', 
                                relief=tk.FLAT,
                                command=lambda:self.SwitchPage(self.page_main.id),
                                font=button_font)
        button_robot_state.place(x=button_width * 2, y=0, width=button_width, height=button_height)
        # button_data.bind("<Enter>", on_enter)
        # button_data.bind("<Leave>", on_leave)
        
        


'''
上位机窗口
'''

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

from lib.log_info import LogError , LogInfo , LogWarning


class Window():
    def __init__(self) -> None:
        self.window = tk.Tk()
        LogInfo("窗口已创建")
        self.version = 'V1.0.0'
        LogInfo('版本已确认：' + self.version)

############################################################
#  主要功能
#  InitApp 初始化程序
#  RunApp 运行程序
#  QuitApp 退出程序
############################################################
    def InitApp(self):
        '''初始化程序'''
        self.InitUI()
        LogInfo('UI已初始化')
    
    def RunApp(self):
        '''运行程序'''
        self.window.mainloop()
    
    def QuitApp(self):
        '''弹出一个弹窗，询问是否退出，如果是则退出，否则不退出'''
        pass
        # quit_app = tkinter.messagebox.askyesno(title='提示', message='是否退出？')
        # if quit_app:#退出程序
        #     if self.serial_port_model.port_is_open:
        #         self.serial_data_read_module.CloseSerialPort()
        #     sys.exit(0)
        
    def BlankFunction(self):
        '''空函数，用于占位'''
        pass

############################################################
#  界面创建
#  InitUI 初始化UI
#  CreateMenu 创建菜单栏
############################################################
    
    def InitUI(self):
        '''初始化UI'''
        self.window.title('StandardRobot++ Tool  ' + self.version)
        self.window.geometry('1200x500')
        self.window.resizable(0,0)
        
        # self.CreateMenu()

    def CreateMenu(self):
        '''创建菜单栏'''
        #菜单栏
        MenuBar = tk.Menu(self.window)
        self.window.config(menu=MenuBar)
        #菜单栏/文件
        Menu_File = tk.Menu(MenuBar, tearoff=0)
        MenuBar.add_cascade(label='文件', menu=Menu_File)
        #菜单栏/文件/打开
        # Menu_File.add_command(label='打开', command=self.BlankFunction)
        #菜单栏/文件/保存
        # Menu_File.add_command(label='保存输入波形图', command=self.SaveInputWaveform_Click)
        # #菜单栏/文件/退出
        # Menu_File.add_command(label='退出', command=self.Quit_App)
        # #菜单栏/帮助
        # Menu_Help = tk.Menu(MenuBar, tearoff=0)
        # MenuBar.add_cascade(label='帮助', menu=Menu_Help)
        # #菜单栏/帮助/如何使用
        # Menu_Help.add_command(label='如何使用', command=hw.RunHowToUse)
        # #菜单栏/帮助/关于
        # Menu_Help.add_command(label='关于程序', command=hw.RunAbout)
        # #菜单栏/帮助/历史版本
        # Menu_Help.add_command(label='历史版本', command=self.BlankFunction)
        # #菜单栏/打赏
        # MenuBar.add_command(label='打赏', command=hw.RunPay)
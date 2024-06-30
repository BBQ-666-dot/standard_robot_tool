'''
上位机窗口
'''

import tkinter as tk
import tkinter.ttk
import tkinter.messagebox

import time

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process
from OperationTypedef import ERROR

from Page_Main import Page_Main
from Page_Debug import Page_Debug
from Page_RobotCmd import Page_Robot_Cmd

class Window():
    def __init__(self, usb:USB_Device, data_process:Data_Process, operations:list, run_time:dict) -> None:
        self.usb = usb
        self.data_process = data_process
        self.operations = operations
        self.run_time = run_time
        
        self.window = tk.Tk()
        LogInfo("窗口已创建")
        self.version = 'V3.0.3'
        LogInfo('版本已确认：' + self.version)
        self.height = 0
        self.width = 0
        
        self.page_main = Page_Main(self.window,
                                   usb=self.usb, 
                                   data_process=self.data_process,
                                   operations=self.operations)
        self.page_debug = Page_Debug(self.window,self.data_process)
        self.page_robot_cmd = Page_Robot_Cmd(self.window)
        
        start_time = int(time.time() * 1000)
        self.run_time['TASK_Window'] = start_time
        LogInfo(f"[{start_time}(ms)]开始运行 StandardRobot++ 上位机的可视化模块")
        self.FeedDog()
        return
    
    def BlankFunction(self):
        '''空函数，用于占位'''
        pass
    
    def FeedDog(self):
        self.run_time['TASK_Window'] = int(time.time() * 1000)
        if not ERROR in self.operations:
            self.window.after(300, self.FeedDog) #300ms后再次调用FeedDog
        else:
            tkinter.messagebox.showerror(title='错误', message='程序出现问题，请关闭')
            self.window.quit()
        return

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
            # return
            self.page_main.lift()
        elif page_id == self.page_debug.id:
            # return
            self.page_debug.lift()
        elif page_id == self.page_robot_cmd.id:
            # return
            self.page_robot_cmd.lift()


    ############################################################
    #  界面创建
    #  InitUI 初始化UI
    #  CreateMenu 创建菜单栏
    #  CreatePages 创建页面
    ############################################################
    
    def InitUI(self):
        '''初始化UI'''
        self.window.title('StandardRobot++ Tool  ' + self.version)
        self.window.geometry(f'{self.width}x{self.height}')
        self.window.resizable(0,0)
        self.CreateMenu()
        self.CreatePages()

    def CreateMenu(self):
        '''创建菜单栏'''
        button_width = 100
        button_height = 50
        
        button_width = self.width / 3
        button_height = 30
        
        button_font = ('黑体', 15)
        
        button_main = tk.Button(self.window, 
                                text='主界面', 
                                relief=tk.FLAT,
                                command=lambda:self.SwitchPage(self.page_main.id),
                                font=button_font)
        button_main.place(x=button_width * 0, y=0, width=button_width, height=button_height)
        
        button_debug = tk.Button(self.window, 
                                text='调试数据', 
                                relief=tk.FLAT,
                                command=lambda:self.SwitchPage(self.page_debug.id),
                                font=button_font)
        button_debug.place(x=button_width * 1, y=0, width=button_width, height=button_height)

        button_robot_cmd = tk.Button(self.window, 
                                text='机体控制', 
                                relief=tk.FLAT,
                                command=lambda:self.SwitchPage(self.page_robot_cmd.id),
                                font=button_font)
        button_robot_cmd.place(x=button_width * 2, y=0, width=button_width, height=button_height)
    
    def CreatePages(self):
        '''创建页面'''
        page_width = self.width
        page_height = self.height - 30
        
        self.page_main.CreatePage(page_width, page_height)
        self.page_debug.CreatePage(page_width, page_height)
        self.page_robot_cmd.CreatePage()
        self.page_main.place(x=0, y=30, width=page_width, height=page_height)
        self.page_debug.place(x=0, y=30, width=page_width, height=page_height)
        self.page_robot_cmd.place(x=0, y=30, width=page_width, height=page_height)
        
        self.SwitchPage(self.page_main.id)



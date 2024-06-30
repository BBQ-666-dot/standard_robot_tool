import tkinter as tk
from tkinter import Canvas
from pynput import keyboard, mouse
# import pygame
# from pygame.locals import *

class Control_Model(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(text='机器人控制信息')
        self.cmd = {
            "vx":0,
            "vy":0,
            "wz":0
        }
        self.AddWidget()
        return

    def AddWidget(self):
        font = ('黑体', 12)
        
        # # 第1行：vx
        label_vx = tk.Label(
                self,
                text='vx: 0 m/s',
                font=font,
                anchor='w'
                )
        label_vx.grid(row=0, column=0)
        
        # 第2行：vy
        label_vy = tk.Label(
                self,
                text='vy: 0 m/s',
                font=font,
                anchor='w'
                )
        label_vy.grid(row=1, column=0)
        
        # 第3行：wz
        label_wz = tk.Label(
                self,
                text='wz: 0 rad/s',
                font=font,
                anchor='w'
                )
        label_wz.grid(row=2, column=0)
        return

class Page_Robot_Cmd(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.id = 3
        self.is_cmd = False
        # pygame.init()
        # pygame.joystick.init()  # 初始化手柄支持
        # joystick_count = pygame.joystick.get_count()
        # if joystick_count > 0:
        #     joystick = pygame.joystick.Joystick(0)  # 假设只有一个手柄连接
        #     joystick.init()
        # else:
        #     print("未检测到手柄！")
        #     exit()
        return
    
    def CreatePage(self,width:int,height:int):
        Control_Model(self).place(x=10, y=10, width=width-20, height=150)
        return
    ############################################################
    #  实时任务
    #  UpdateRobotCmdInfo 更新机器人控制信息
    ############################################################
    def UpdateRobotCmdInfo(self):
        return
    
    ############################################################
    #  用户接口
    #  StartCmd
    #  StopCmd
    ############################################################
    def StartCmd(self):
        self.is_cmd = True
        return

    def StopCmd(self):
        self.is_cmd = False
        return


    
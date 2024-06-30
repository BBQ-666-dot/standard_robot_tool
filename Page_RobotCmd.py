import tkinter as tk
from tkinter import Canvas
# import pygame
# from pygame.locals import *

class Control_Model(tk.LabelFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(text='机器人控制信息')
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
        
        # entry_vx = tk.Entry(
        #         self,
        #         font=font,
        #         width=10
        #         )
        # entry_vx.grid(row=0, column=1)
        
        # scale_vx = tk.Scale(
        #         self,
        #         from_=-100,
        #         to=100,
        #         orient='horizontal',
        #         font=font
        #         )
        # scale_vx.grid(row=0, column=2)
        
        # 第2行：vy
        label_vy = tk.Label(
                self,
                text='vy: 0 m/s',
                font=font,
                anchor='w'
                )
        label_vy.grid(row=1, column=0)
        
        # entry_vy = tk.Entry(
        #         self,
        #         font=font,
        #         width=10
        #         )
        # entry_vy.grid(row=1, column=1)
        
        # scale_vy = tk.Scale(
        #         self,
        #         from_=-100,
        #         to=100,
        #         orient='horizontal',
        #         font=font
        #         )
        # scale_vy.grid(row=1, column=2)
        
        # 第3行：wz
        label_wz = tk.Label(
                self,
                text='wz: 0 rad/s',
                font=font,
                anchor='w'
                )
        label_wz.grid(row=2, column=0)
        
        # entry_wz = tk.Entry(
        #         self,
        #         font=font,
        #         width=10
        #         )
        # entry_wz.grid(row=2, column=1)
        
        # scale_wz = tk.Scale(
        #         self,
        #         from_=-100,
        #         to=100,
        #         orient='horizontal',
        #         # font=font
        #         )
        # scale_wz.grid(row=2, column=2)
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


    
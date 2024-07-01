import tkinter as tk
from tkinter import Canvas
from pynput import keyboard, mouse
# import pygame
# from pygame.locals import *

class Control_Model(tk.LabelFrame):
    def __init__(self, master, robot_cmd:dict, **kwargs):
        super().__init__(master, **kwargs)
        self.config(text='机器人控制信息')
        self.robot_cmd = robot_cmd
        self.AddWidget()
        self.after(10, self.Update) # 10ms后更新
        return

    def AddWidget(self):
        font = ('黑体', 12)
        
        # # 第1行：vx
        self.label_vx = tk.Label(
                self,
                text='vx: 0 m/s',
                font=font,
                anchor='w'
                )
        self.label_vx.grid(row=0, column=0)
        
        # 第2行：vy
        self.label_vy = tk.Label(
                self,
                text='vy: 0 m/s',
                font=font,
                anchor='w'
                )
        self.label_vy.grid(row=1, column=0)
        
        # 第3行：wz
        self.label_wz = tk.Label(
                self,
                text='wz: 0 rad/s',
                font=font,
                anchor='w'
                )
        self.label_wz.grid(row=2, column=0)
        
        # 第4行：gimbal pitch
        self.label_gimbal_pitch = tk.Label(
                self,
                text='gimbal_pitch: 0 rad',
                font=font,
                anchor='w'
                )
        self.label_gimbal_pitch.grid(row=3, column=0)
        
        # 第5行：gimbal yaw
        self.label_gimbal_yaw = tk.Label(
                self,
                text='gimbal_yaw: 0 rad',
                font=font,
                anchor='w'
                )
        self.label_gimbal_yaw.grid(row=4, column=0)
        return
    
    def Update(self):
        self.label_vx.config(text=f'vx: {self.robot_cmd["speed_vector"]["vx"]:.3f} m/s')
        self.label_vy.config(text=f'vy: {self.robot_cmd["speed_vector"]["vy"]:.3f} m/s')
        self.label_wz.config(text=f'wz: {self.robot_cmd["speed_vector"]["wz"]:.3f} rad/s')
        
        self.label_gimbal_pitch.config(text=f'gimbal_pitch: {self.robot_cmd["gimbal"]["pitch"]:.3f} rad')
        self.label_gimbal_yaw.config(text=f'gimbal_yaw: {self.robot_cmd["gimbal"]["yaw"]:.3f} rad')
        
        self.after(10, self.Update) # 10ms后更新
        return

class Page_Robot_Cmd(tk.Frame):
    def __init__(self, master, robot_cmd:dict, **kwargs):
        super().__init__(master, **kwargs)
        self.id = 3
        self.is_cmd = False
        self.robot_cmd = robot_cmd
        
        self.control_model = Control_Model(self,self.robot_cmd)
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
        self.control_model.place(x=10, y=10, width=width-20, height=150)
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


    
import tkinter as tk
import tkinter.ttk as ttk

import theme
from lib.data_procecss import Data_Process
from lib.log_info import LogInfo
from pynput import keyboard, mouse
# import pygame
# from pygame.locals import *

class Control_Model(tk.LabelFrame):
    def __init__(self, master, robot_cmd:dict, data_process:Data_Process, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(text=" 机器人控制信息 ", bg=theme.CARD, fg=theme.FG_DIM,
                       font=theme.FONT_SM, bd=0, labelanchor="nw",
                       highlightthickness=1, highlightbackground=theme.BORDER)
        self.robot_cmd = robot_cmd
        self.data_process = data_process
        self.value_labels = {}
        self.AddWidget()
        self.after(100, self.Update) # 100ms后更新
        return

    def AddWidget(self):
        rows = [
            ('vx',           '底盘 VX',      'm/s'),
            ('vy',           '底盘 VY',      'm/s'),
            ('wz',           '底盘 WZ',      'rad/s'),
            ('gimbal_pitch', '云台 PITCH',   'rad'),
            ('gimbal_yaw',   '云台 YAW',     'rad'),
        ]
        for i, (key, name, unit) in enumerate(rows):
            y = 24 + i * 54
            theme.label(self, name, dim=True).place(x=24, y=y + 8, width=120, anchor="w")
            value = theme.label(self, '0.000', bold=True, mono=True)
            value.place(x=160, y=y, anchor="w")
            theme.label(self, unit, dim=True, font=theme.FONT_SM).place(x=310, y=y + 8, anchor="w")
            self.value_labels[key] = value
        return
    
    def Update(self):
        cmd = self.robot_cmd
        self.value_labels['vx'].config(text=f"{cmd['speed_vector']['vx']:.3f}")
        self.value_labels['vy'].config(text=f"{cmd['speed_vector']['vy']:.3f}")
        self.value_labels['wz'].config(text=f"{cmd['speed_vector']['wz']:.3f}")
        self.value_labels['gimbal_pitch'].config(text=f"{cmd['gimbal']['pitch']:.3f}")
        self.value_labels['gimbal_yaw'].config(text=f"{cmd['gimbal']['yaw']:.3f}")

        self.after(100, self.Update) # 100ms后更新
        return

class Page_Robot_Cmd(tk.Frame):
    def __init__(self, master, robot_cmd:dict, data_process:Data_Process, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=theme.BG)
        self.id = 3
        self.is_active = False
        self.is_cmd = False
        self.robot_cmd = robot_cmd
        self.data_process = data_process
        
        self.control_model = Control_Model(self,self.robot_cmd,self.data_process)
        return
    
    def CreatePage(self,width:int,height:int):
        self.control_model.place(x=16, y=16, width=580, height=330)

        # 发送设置卡片
        send = theme.card(self, "发送设置")
        send.place(x=612, y=16, width=width-628, height=330)
        self.send_card = send

        self.send_status_dot = tk.Canvas(send, width=18, height=18, bg=theme.CARD,
                                         highlightthickness=0)
        self.send_status_dot.place(x=24, y=30)
        self.send_dot_item = self.send_status_dot.create_oval(3, 3, 15, 15,
                                                              fill=theme.FG_DIM, outline="")
        self.send_status_label = theme.label(send, "未发送", bold=True)
        self.send_status_label.place(x=52, y=30, anchor="w")

        theme.label(send, "发送频率", dim=True).place(x=24, y=84)
        self.combobox_rate = ttk.Combobox(send, values=['50 Hz', '100 Hz', '200 Hz', '500 Hz'],
                                          state='readonly', width=8,
                                          font=theme.FONT_TXT, style="Dark.TCombobox")
        self.combobox_rate.current(2)
        self.combobox_rate.place(x=110, y=78, width=100, height=30)
        self.combobox_rate.bind('<<ComboboxSelected>>', self.OnRateChanged)

        theme.label(send, "已发送", dim=True).place(x=24, y=132)
        self.sent_label = theme.label(send, '0', bold=True, mono=True)
        self.sent_label.place(x=110, y=128, anchor="w")

        self.button_toggle_send = theme.button(send, text='开始发送',
                                               command=self.ToggleSend, accent=True)
        self.button_toggle_send.place(x=24, y=180, width=186, height=40)

        # 键鼠/手柄控制开关
        self.input_enabled = tk.IntVar(value=1)
        self.checkbutton_input = tk.Checkbutton(send, text='键鼠 / 手柄控制',
                                                variable=self.input_enabled,
                                                bg=theme.CARD, fg=theme.FG,
                                                activebackground=theme.CARD,
                                                activeforeground=theme.FG,
                                                selectcolor=theme.CARD_HI,
                                                font=theme.FONT_TXT,
                                                highlightthickness=0, bd=0,
                                                anchor="w",
                                                command=self.OnInputEnabledChanged)
        self.checkbutton_input.place(x=24, y=234, width=186, height=28)

        theme.label(send, "切到本页自动发送\n切走自动停止", dim=True,
                    font=theme.FONT_SM, justify="left").place(x=24, y=272)

        # 快捷操作卡片
        quick = theme.card(self, "快捷操作")
        quick.place(x=16, y=362, width=width-32, height=100)
        theme.button(quick, text='摩擦轮 开', command=lambda: self.SetFric(True)).place(x=24, y=30, width=140, height=40)
        theme.button(quick, text='摩擦轮 关', command=lambda: self.SetFric(False)).place(x=178, y=30, width=140, height=40)
        theme.button(quick, text='开火', command=self.FireOnce).place(x=332, y=30, width=140, height=40)
        theme.button(quick, text='一键清零', command=self.ClearCmd).place(x=486, y=30, width=160, height=40)
        theme.label(quick, "快捷操作直接修改下发的指令值，键鼠/手柄移动会覆盖", dim=True,
                    font=theme.FONT_SM).place(x=670, y=42)

        # 控制说明卡片
        hint = theme.card(self, "控制说明")
        hint.place(x=16, y=478, width=width-32, height=height-494)
        lines = [
            "键鼠：W / S 前后，A / D 左右，Q / E 底盘旋转，鼠标控制云台俯仰与偏航。",
            "手柄：左摇杆控制底盘平移，右摇杆控制云台，扳机键控制发射。",
            "控制指令通过 USB 虚拟串口下发，频率、通道值需与下位机参数匹配。",
            "发送前请确认机器人处于安全状态（架空或垫起轮子）。",
        ]
        y = 26
        for text in lines:
            theme.label(hint, "· " + text, dim=True).place(x=24, y=y, anchor="w")
            y += 30

        self.after(200, self.UpdateSendState)
        return

    ############################################################
    #  实时任务
    #  UpdateSendState 更新发送状态
    ############################################################
    def UpdateSendState(self):
        sending = self.data_process.sending_data
        if sending:
            self.send_status_dot.itemconfigure(self.send_dot_item, fill=theme.OK)
            self.send_status_label.configure(text="发送中")
            self.button_toggle_send.configure(text='停止发送')
        else:
            self.send_status_dot.itemconfigure(self.send_dot_item, fill=theme.FG_DIM)
            self.send_status_label.configure(text="未发送")
            self.button_toggle_send.configure(text='开始发送')
        self.sent_label.configure(text=f"{self.data_process.stats['tx_packets']}")
        self.after(200, self.UpdateSendState)
        return

    ############################################################
    #  回调函数
    #  ToggleSend 发送开关
    #  OnRateChanged 频率切换
    ############################################################
    def ToggleSend(self):
        if self.data_process.sending_data:
            self.data_process.stop_send()
            LogInfo("已停止发送控制指令")
        else:
            self.data_process.start_send()
            LogInfo("已开始发送控制指令")
        return

    def OnRateChanged(self, event=None):
        try:
            hz = int(self.combobox_rate.get().split()[0])
            if hz > 0:
                self.data_process.send_period = 1.0 / hz
                LogInfo(f"发送频率已设置为 {hz} Hz")
        except Exception:
            pass
        return

    def OnInputEnabledChanged(self):
        from TASK_Listen import set_input_enabled
        enabled = (self.input_enabled.get() == 1)
        set_input_enabled(enabled, self.robot_cmd)
        LogInfo("键鼠/手柄控制已开启" if enabled else "键鼠/手柄控制已关闭")
        return

    ############################################################
    #  快捷操作
    #  SetFric    摩擦轮开关
    #  FireOnce   单次开火(150ms脉冲)
    #  ClearCmd   一键清零所有控制指令
    ############################################################
    def SetFric(self, on:bool):
        self.robot_cmd['shoot']['fric_on'] = 1 if on else 0
        LogInfo("摩擦轮已开" if on else "摩擦轮已关")
        return

    def FireOnce(self):
        self.robot_cmd['shoot']['fire'] = 1
        LogInfo("已发送开火指令")
        self.after(150, lambda: self.robot_cmd['shoot'].update({'fire': 0}))
        return

    def ClearCmd(self):
        cmd = self.robot_cmd
        cmd['speed_vector']['vx'] = 0
        cmd['speed_vector']['vy'] = 0
        cmd['speed_vector']['wz'] = 0
        cmd['gimbal']['yaw'] = 0
        cmd['gimbal']['pitch'] = 0
        cmd['chassis']['roll'] = 0
        cmd['shoot']['fire'] = 0
        cmd['shoot']['fric_on'] = 0
        LogInfo("已清零所有控制指令")
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

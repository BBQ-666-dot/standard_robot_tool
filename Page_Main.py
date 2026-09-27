import math
import time
import tkinter as tk
import tkinter.ttk as ttk

import theme
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process
from lib.log_info import LogInfo
from OperationTypedef import OPEN_USB, CLOSE_USB
from CustomWidget import PostureGraphModel

class SerialModel(tk.LabelFrame):
    def __init__(self, master, usb:USB_Device, operations:list, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(text=" 串口连接 ", bg=theme.CARD, fg=theme.FG_DIM,
                       font=theme.FONT_SM, bd=0, labelanchor="nw",
                       highlightthickness=1, highlightbackground=theme.BORDER)
        self.operations = operations
        self.usb = usb
        self.port_is_open = False
        self.auto_reconnect = tk.IntVar(value=0)
        self.last_opened_port = None
        self.last_reconnect_time = 0.0
        self.AddWidget()
        self.CheckPort()
        self.UpdateSerialPortList()
        return
    
    def AddWidget(self):
        # 端口号
        theme.label(self, "端口号", dim=True).place(x=16, y=18)

        available_ports = self.usb.get()
        port_name_list = [p[0] for p in available_ports] if len(available_ports) > 0 else ['无可用端口']
        self.combobox_port = ttk.Combobox(
                        self,
                        font=theme.FONT_TXT,
                        values = port_name_list,
                        postcommand = self.UpdateSerialPortList,
                        state='readonly',
                        style="Dark.TCombobox"
                    )
        self.combobox_port.place(x=80, y=15, width=140, height=28)
        self.combobox_port.current(0)

        # 状态指示灯 + 开关按钮
        self.status_dot = tk.Canvas(self, width=16, height=16, bg=theme.CARD,
                                    highlightthickness=0)
        self.status_dot.place(x=18, y=74)
        self.dot_item = self.status_dot.create_oval(3, 3, 13, 13,
                                                    fill=theme.ERR, outline="")

        self.button_toggle_Port = theme.button(self, text='打开端口',
                                               command=self.TogglePort)
        self.button_toggle_Port.place(x=80, y=64, width=140, height=34)

        self.checkbutton_reconnect = tk.Checkbutton(self, text='断线自动重连',
                                                    variable=self.auto_reconnect,
                                                    bg=theme.CARD, fg=theme.FG,
                                                    activebackground=theme.CARD,
                                                    activeforeground=theme.FG,
                                                    selectcolor=theme.CARD_HI,
                                                    font=theme.FONT_SM,
                                                    highlightthickness=0, bd=0,
                                                    anchor="w")
        self.checkbutton_reconnect.place(x=14, y=112, width=150, height=24)
        theme.label(self, "选新出现的串口", dim=True,
                    font=theme.FONT_SM).place(x=166, y=116)
        return

    ############################################################
    #  实时任务
    #  CheckPort 检测串口状态
    #  UpdateSerialPortList 更新串口列表
    ############################################################
    def CheckPort(self):
        if self.usb.is_open != self.port_is_open: # 只在状态变化时更新UI
            self.port_is_open = self.usb.is_open
            self.status_dot.itemconfigure(
                self.dot_item,
                fill=theme.OK if self.port_is_open else theme.ERR)
            self.button_toggle_Port.configure(
                text='关闭端口' if self.port_is_open else '打开端口')
            if self.port_is_open:
                self.last_opened_port = self.usb.port

        # 断线自动重连: 只重连成功打开过的端口, 3s一次
        if (self.auto_reconnect.get() == 1) and (not self.usb.is_open) \
                and self.last_opened_port \
                and (OPEN_USB not in self.operations) \
                and (CLOSE_USB not in self.operations):
            now = time.time()
            if now - self.last_reconnect_time > 3.0:
                ports = [p[0] for p in self.usb.get()]
                if self.last_opened_port in ports:
                    self.last_reconnect_time = now
                    self.usb.modify(self.last_opened_port, 9600, 8, 1, "N")
                    self.operations.append(OPEN_USB)
                    LogInfo(f"尝试自动重连 {self.last_opened_port}")

        self.after(200, self.CheckPort)# 200ms后检查串口状态
        return
    
    def UpdateSerialPortList(self):
        '''更新串口列表'''
        available_ports = self.usb.get()
        port_name_list = [p[0] for p in available_ports] if len(available_ports) > 0 else ['无可用端口']
        if list(self.combobox_port.cget('values')) != port_name_list:
            self.combobox_port.configure(values=port_name_list)
            if self.combobox_port.get() not in port_name_list:
                self.combobox_port.current(0)

        self.after(2000, self.UpdateSerialPortList)# 2s后更新串口列表
        return

    ############################################################
    #  回调函数
    #  TogglePort 变更串口状态
    ############################################################
    def TogglePort(self):
        # 上一次开/关操作还没被后台线程处理完时，忽略连点，避免操作堆积
        if OPEN_USB in self.operations or CLOSE_USB in self.operations:
            return
        if not self.usb.is_open:
            if self.combobox_port.get() == '无可用端口':
                return
            self.usb.modify(self.combobox_port.get(),9600,8,1,"N")
            self.operations.append(OPEN_USB)
        else:
            self.operations.append(CLOSE_USB)
        return

class Robot_Info_Model(tk.LabelFrame):
    def __init__(self, master, data_process:Data_Process, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(text=" 机器人信息 ", bg=theme.CARD, fg=theme.FG_DIM,
                       font=theme.FONT_SM, bd=0, labelanchor="nw",
                       highlightthickness=1, highlightbackground=theme.BORDER)
        self.data_process = data_process
        self.value_labels = {}
        self.AddWidget()
        self.after(200, self.UpdateRobotInfo)# 200ms后更新机器人信息
        return
    
    def AddWidget(self):
        rows = [
            ('run_time',          '设备运行时间'),
            ('chassis',           '底盘'),
            ('gimbal',            '云台'),
            ('shoot',             '发射机构'),
            ('arm',               '机械臂'),
        ]
        for i, (key, text) in enumerate(rows):
            y = 20 + i * 40
            theme.label(self, text, dim=True).place(x=16, y=y + 3, width=110, anchor="w")
            value = theme.label(self, '--', bold=True)
            value.place(x=132, y=y, anchor="w")
            self.value_labels[key] = value
        return

    ############################################################
    #  实时任务
    #  UpdateRobotInfo 更新机器人信息
    ############################################################

    def UpdateRobotInfo(self):
        chassis_names = ['无底盘','麦轮底盘','全向轮底盘','舵轮底盘','平衡底盘']
        gimbal_names = ['无云台','yaw-pitch直连云台']
        shoot_names = ['无发射机构','摩擦轮+拨弹盘','气动+拨弹盘']
        arm_names = ['无机械臂','企鹅mini机械臂']

        def pick(names, index):
            try:
                return names[int(index) % len(names)]
            except Exception:
                return '--'

        latest = self.data_process.robot_info_data.latest
        types = latest['types']
        self.value_labels['run_time'].config(
            text=f"{int(latest['time_stamp']) / 1000:.0f} s")
        self.value_labels['chassis'].config(text=pick(chassis_names, types['chassis']))
        self.value_labels['gimbal'].config(text=pick(gimbal_names, types['gimbal']))
        self.value_labels['shoot'].config(text=pick(shoot_names, types['shoot']))
        self.value_labels['arm'].config(text=pick(arm_names, types['arm']))

        self.after(200, self.UpdateRobotInfo)# 200ms后更新机器人信息
        return


class Page_Main(tk.Frame):
    def __init__(self, master, usb:USB_Device, data_process:Data_Process, operations:list, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=theme.BG)
        self.id = 1
        self.is_active = True
        self.operations = operations
        self.data_process = data_process
        self.usb = usb
        self.imu_values = {}
        self.imu_unit_labels = []
        self.unit_deg = True
        self.stat_values = {}
        self.label_tick = 0
        self.last_thetas = (None, None, None)
        self.idle_frames = 0
        self.after(16, self.UpdateImuPos)# 16ms(约60FPS)更新IMU姿态信息
    
    def CreatePage(self,width:int,height:int):
        '''主页包含: 串口连接 / IMU姿态 / IMU数值 / 机器人信息 / 数据统计'''

        # 左列
        SerialModel(self,
                   usb = self.usb,
                   operations = self.operations
                   ).place(x=16, y=16, width=300, height=150)

        Robot_Info_Model(self,
                        data_process = self.data_process
                        ).place(x=16, y=182, width=300, height=250)

        self.CreateTips(16, 448, 300, height-464)

        # 中列: IMU姿态 + 数值
        self.pos_graph_model = PostureGraphModel(self)
        self.pos_graph_model.place(x=332, y=16, width=440, height=440)
        self.CreateImuPanel(332, 472, 440, height-488)

        # 右列: 数据统计
        self.CreateStatsPanel(788, 16, width-804, height-32)
        return

    def CreateImuPanel(self, x, y, w, h):
        card = theme.card(self, "IMU 数值")
        card.place(x=x, y=y, width=w, height=h)
        self.imu_card = card

        # 单位切换(deg <-> rad)
        self.unit_button = theme.button(card, text='单位: °', command=self.ToggleImuUnit)
        self.unit_button.place(x=w-102, y=10, width=88, height=26)

        cells = [
            ('roll',  'ROLL',  '°',   16),
            ('pitch', 'PITCH', '°',   162),
            ('yaw',   'YAW',   '°',   308),
        ]
        gyro_cells = [
            ('gx', 'GYRO X', '°/s', 16),
            ('gy', 'GYRO Y', '°/s', 162),
            ('gz', 'GYRO Z', '°/s', 308),
        ]
        for key, name, unit, cx in cells:
            theme.label(card, name, dim=True, font=theme.FONT_SM).place(x=cx, y=22)
            label = theme.label(card, '0.0', bold=True, mono=True)
            label.place(x=cx, y=40)
            unit_label = theme.label(card, unit, dim=True, font=theme.FONT_SM)
            unit_label.place(x=cx+90, y=50)
            self.imu_unit_labels.append(unit_label)
            self.imu_values[key] = label
        tk.Frame(card, bg=theme.BORDER, height=1).place(x=12, y=88,
                                                        width=w-24, height=1)
        for key, name, unit, cx in gyro_cells:
            theme.label(card, name, dim=True, font=theme.FONT_SM).place(x=cx, y=102)
            label = theme.label(card, '0.0', bold=True, mono=True)
            label.place(x=cx, y=120)
            unit_label = theme.label(card, unit, dim=True, font=theme.FONT_SM)
            unit_label.place(x=cx+90, y=130)
            self.imu_unit_labels.append(unit_label)
            self.imu_values[key] = label
        return

    def ToggleImuUnit(self):
        self.unit_deg = not self.unit_deg
        self.unit_button.configure(text='单位: °' if self.unit_deg else '单位: rad')
        for label in self.imu_unit_labels[:3]:
            label.configure(text='°' if self.unit_deg else 'rad')
        for label in self.imu_unit_labels[3:]:
            label.configure(text='°/s' if self.unit_deg else 'rad/s')
        LogInfo(f"IMU 显示单位切换为 {'deg' if self.unit_deg else 'rad'}")
        return

    def CreateStatsPanel(self, x, y, w, h):
        card = theme.card(self, "数据统计")
        card.place(x=x, y=y, width=w, height=h)

        rows = [
            ('frames', '接收帧数'),
            ('rx_kb',  '接收数据'),
            ('errors', '错误帧'),
            ('tx',     '发送包'),
            ('demo',   '演示模式'),
            ('uptime', '运行时间'),
        ]
        for i, (key, text) in enumerate(rows):
            yy = 22 + i * 38
            theme.label(card, text, dim=True).place(x=16, y=yy + 3, anchor="w")
            value = theme.label(card, '--', bold=True)
            value.place(x=120, y=yy, anchor="w")
            self.stat_values[key] = value

        theme.label(card, "按 F5 可切换\n演示数据", dim=True,
                    font=theme.FONT_SM, justify="left").place(x=16, y=h-70)
        return

    def CreateTips(self, x, y, w, h):
        card = theme.card(self, "使用提示")
        card.place(x=x, y=y, width=w, height=h)
        tips = [
            ("USB 连接", "插上 C 板后选择新出现的串口"),
            ("F1 ~ F5", "快速切换页面"),
            ("F6", "开关演示数据（无C板预览）"),
            ("通信监控", "各电机/模块在线状态与丢包超时"),
        ]
        yy = 14
        for title, text in tips:
            theme.label(card, title, bold=True).place(x=16, y=yy, anchor="w")
            theme.label(card, text, dim=True, font=theme.FONT_SM).place(x=16, y=yy + 20, anchor="w")
            yy += 42
        return
    
    ############################################################
    #  实时任务
    #  UpdateImuPos 更新IMU姿态信息
    ############################################################
    
    def UpdateImuPos(self):
        interval = 16
        if self.is_active:
            latest = self.data_process.imu_data.latest
            thetas = {
                "yaw": latest['yaw'],
                "pitch": latest['pitch'],
                "roll": latest['roll']
            }
            changed = (self.last_thetas[0] is None or
                       abs(thetas['yaw'] - self.last_thetas[0]) > 1e-7 or
                       abs(thetas['pitch'] - self.last_thetas[1]) > 1e-7 or
                       abs(thetas['roll'] - self.last_thetas[2]) > 1e-7)
            if changed:
                self.idle_frames = 0
                self.last_thetas = (thetas['yaw'], thetas['pitch'], thetas['roll'])
                self.pos_graph_model.UpdateGraph(thetas)

                # 数值/统计面板每3帧刷新一次, 降低UI开销
                self.label_tick = (self.label_tick + 1) % 3
                if self.label_tick == 0:
                    if self.unit_deg:
                        for key in ('roll', 'pitch', 'yaw'):
                            self.imu_values[key].config(text=f"{math.degrees(latest[key]):+7.1f}")
                        for key, gyro_key in (('gx', 'roll_vel'), ('gy', 'pitch_vel'), ('gz', 'yaw_vel')):
                            self.imu_values[key].config(
                                text=f"{math.degrees(latest[gyro_key]):+7.1f}")
                    else:
                        for key in ('roll', 'pitch', 'yaw'):
                            self.imu_values[key].config(text=f"{latest[key]:+7.3f}")
                        for key, gyro_key in (('gx', 'roll_vel'), ('gy', 'pitch_vel'), ('gz', 'yaw_vel')):
                            self.imu_values[key].config(text=f"{latest[gyro_key]:+7.3f}")

                    stats = self.data_process.stats
                    self.stat_values['frames'].config(text=f"{stats['rx_frames']}")
                    self.stat_values['rx_kb'].config(text=f"{self.usb.rx_bytes/1024:.1f} KB")
                    self.stat_values['errors'].config(text=f"{stats['rx_errors']}")
                    self.stat_values['tx'].config(text=f"{stats['tx_packets']}")
                    self.stat_values['demo'].config(
                        text='开' if stats['demo'] else '关',
                        fg=theme.OK if stats['demo'] else theme.FG_DIM)
                    uptime = int(self.data_process.robot_info_data.latest['time_stamp'])
                    self.stat_values['uptime'].config(text=f"{uptime/1000:.0f} s")
            else:
                # 数据静止: 降低刷新率省CPU
                self.idle_frames += 1
                if self.idle_frames > 10:
                    interval = 100
        self.after(interval, self.UpdateImuPos)# 16ms(约60FPS)更新IMU姿态信息

'''
通信监控页
- 模块通信状态(下位机上报: 各电机/模块在线标志)
- 数据包监控(上位机统计: 每个包id的速率/超时/总数/最后接收)
'''
import time
import tkinter as tk

import theme
from lib.data_procecss import Data_Process
from lib.log_info import LogInfo, LogWarning

# (数据包id, 名称)
PACKETS = [
    (0x02, 'IMU 数据'),
    (0x03, '机器人状态'),
    (0x01, '调试数据'),
    (0x1D, '云台关节电机'),
    (0x1E, '底盘运动反馈'),
    (0x0F, '发射机构'),
    (0x0A, '机器人状态(裁判)'),
    (0x04, '比赛状态(裁判)'),
    (0x06, '血量(裁判)'),
    (0x08, '裁判警告'),
    (0x0D, 'BUFF(裁判)'),
    (0x11, 'RFID(裁判)'),
    (0x13, '地面机器人(裁判)'),
]

# 下位机调试变量里的模块在线标志(0/1)
MODULES = [
    ('motor1',   '底盘电机 1'),
    ('motor2',   '底盘电机 2'),
    ('motor3',   '底盘电机 3'),
    ('motor4',   '底盘电机 4'),
    ('gimbal_y', '云台 YAW 电机'),
    ('gimbal_p', '云台 PITCH 电机'),
    ('trigger',  '拨弹电机'),
    ('referee',  '裁判系统'),
    ('bmi088',   'IMU (BMI088)'),
    ('remote_rc', '遥控接收'),
]


class Page_Monitor(tk.Frame):
    def __init__(self, master, data_process:Data_Process, usb=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.configure(bg=theme.BG)
        self.id = 4
        self.is_active = False
        self.data_process = data_process
        self.usb = usb
        self.online_state = {}
        self.module_state = {}
        self.miss_count = {}
        self.first_seen = {}
        self.last_errors = 0
        self.module_rows = {}
        self.packet_rows = {}
        self.after(500, self.Update)

    def CreatePage(self, width:int, height:int) -> None:
        # 模块通信状态
        module_card = theme.card(self, "模块通信（下位机上报）")
        module_card.place(x=16, y=16, width=430, height=height-32)
        for i, (key, name) in enumerate(MODULES):
            y = 20 + i * 48
            canvas = tk.Canvas(module_card, width=16, height=16, bg=theme.CARD,
                               highlightthickness=0)
            canvas.place(x=18, y=y + 2)
            item = canvas.create_oval(3, 3, 13, 13, fill=theme.FG_DIM, outline="")
            theme.label(module_card, name, dim=True).place(x=44, y=y, anchor="w")
            value = theme.label(module_card, '--', bold=True)
            value.place(x=280, y=y, anchor="w")
            self.module_rows[key] = (canvas, item, value)

        # 数据包监控
        packet_card = theme.card(self, "数据包监控（上位机统计）")
        packet_card.place(x=462, y=16, width=width-478, height=height-32)
        theme.label(packet_card, "数据包", dim=True, font=theme.FONT_SM).place(x=30, y=10)
        theme.label(packet_card, "速率", dim=True, font=theme.FONT_SM).place(x=210, y=10)
        theme.label(packet_card, "总数", dim=True, font=theme.FONT_SM).place(x=300, y=10)
        theme.label(packet_card, "最后接收", dim=True, font=theme.FONT_SM).place(x=390, y=10)
        for i, (data_id, name) in enumerate(PACKETS):
            y = 42 + i * 40
            canvas = tk.Canvas(packet_card, width=14, height=14, bg=theme.CARD,
                               highlightthickness=0)
            canvas.place(x=16, y=y + 3)
            item = canvas.create_oval(2, 2, 12, 12, fill=theme.FG_DIM, outline="")
            theme.label(packet_card, f"{name}  (0x{data_id:02X})",
                        dim=True, font=theme.FONT_SM).place(x=38, y=y, anchor="w")
            rate = theme.label(packet_card, '--', font=theme.FONT_SM)
            rate.place(x=210, y=y, anchor="w")
            total = theme.label(packet_card, '0', font=theme.FONT_SM)
            total.place(x=300, y=y, anchor="w")
            age = theme.label(packet_card, '未收到', font=theme.FONT_SM)
            age.place(x=390, y=y, anchor="w")
            self.packet_rows[data_id] = (canvas, item, rate, total, age)
        return

    ############################################################
    #  实时任务
    #  Update 更新状态 + 异常检测
    ############################################################
    def Update(self):
        now = time.time()
        stats = self.data_process.stats

        # 是否有数据源在跑: 演示模式 或 串口已连接。
        # 没有数据源时, 不显示任何"在线", 也不做异常判定(避免误报)
        monitoring_active = stats['demo'] or (self.usb is not None and self.usb.is_open)

        # 1. 模块通信状态(下位机调试变量, 且要求数据新鲜)
        debug_entry = stats['ids'].get(0x01)
        debug_fresh = (debug_entry is not None and
                       (now - debug_entry['last']) < 2.0 and monitoring_active)
        if debug_fresh:
            datas = self.data_process.debug_data.latest.get('datas', {})
        else:
            datas = {}
            self.module_state.clear()

        for key, name in MODULES:
            if key not in self.module_rows:
                continue
            canvas, item, value = self.module_rows[key]
            if key not in datas:
                canvas.itemconfigure(item, fill=theme.FG_DIM)
                value.configure(text='--', fg=theme.FG_DIM)
                continue
            online = datas[key] >= 0.5
            canvas.itemconfigure(item, fill=theme.OK if online else theme.ERR)
            value.configure(text='在线' if online else '离线',
                            fg=theme.OK if online else theme.ERR)

            # 模块掉线/恢复检测(仅告警)
            if key not in self.module_state:
                self.module_state[key] = online
            elif self.module_state[key] and (not online):
                self.module_state[key] = False
                LogWarning(f"模块异常: {name} 离线")
            elif (not self.module_state[key]) and online:
                self.module_state[key] = True
                LogInfo(f"模块恢复: {name} 在线")

        # 2. 数据包监控 + 超时检测
        if not monitoring_active:
            # 无数据源: 状态复位, 列表显示 -- , 不做判定
            self.online_state.clear()
            self.miss_count.clear()
            self.first_seen.clear()
            self.last_errors = stats['rx_errors']
        for data_id, name in PACKETS:
            if data_id not in self.packet_rows:
                continue
            canvas, item, rate_label, total_label, age_label = self.packet_rows[data_id]
            entry = stats['ids'].get(data_id)
            if (entry is None) or (not monitoring_active):
                canvas.itemconfigure(item, fill=theme.FG_DIM)
                rate_label.configure(text='--')
                total_label.configure(text='0' if entry is None else f"{entry['count']}")
                age_label.configure(text='未收到' if entry is None else '无数据源',
                                    fg=theme.FG_DIM)
                continue

            age = now - entry['last']
            period = max(entry['period'], 1e-3)
            timeout = max(0.5, period * 6.0)
            # 首次见到该包后5s内为宽限期(启动时线程抢占可能造成瞬断, 不判异常)
            if data_id not in self.first_seen:
                self.first_seen[data_id] = now
            if (now - self.first_seen[data_id]) < 5.0:
                self.miss_count[data_id] = 0
                online = True
            else:
                # 连续2次(1s)超时才判定掉线
                if age <= timeout:
                    self.miss_count[data_id] = 0
                else:
                    self.miss_count[data_id] = self.miss_count.get(data_id, 0) + 1
                online = (age <= timeout) or (self.miss_count.get(data_id, 0) < 2)

            canvas.itemconfigure(item, fill=theme.OK if online else theme.ERR)
            rate_label.configure(text=f"{1.0 / period:6.1f} Hz")
            total_label.configure(text=f"{entry['count']}")
            if online:
                age_label.configure(text=f"{age * 1000:5.0f} ms", fg=theme.FG_DIM)
            else:
                age_label.configure(text=f"{age:5.1f} s", fg=theme.ERR)

            # 异常/恢复检测(仅告警)
            if data_id not in self.online_state:
                self.online_state[data_id] = online
            elif self.online_state[data_id] and (not online):
                self.online_state[data_id] = False
                LogWarning(f"通信异常: {name}(0x{data_id:02X}) 已 {age:.1f}s 无数据")
            elif (not self.online_state[data_id]) and online:
                self.online_state[data_id] = True
                LogInfo(f"通信恢复: {name}(0x{data_id:02X})")

        # 3. 校验错误统计
        if monitoring_active and stats['rx_errors'] > self.last_errors:
            delta = stats['rx_errors'] - self.last_errors
            self.last_errors = stats['rx_errors']
            LogWarning(f"校验错误 +{delta} (累计 {stats['rx_errors']})")

        self.after(500, self.Update)
        return

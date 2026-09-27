'''
上位机窗口
'''

import tkinter as tk
import tkinter.ttk
import tkinter.messagebox

import time

import theme
from lib.log_info import LogError , LogInfo , LogWarning , set_sink
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process
from OperationTypedef import ERROR

from Page_Main import Page_Main
from Page_Debug import Page_Debug
from Page_RobotCmd import Page_Robot_Cmd
from Page_Log import Page_Log
from Page_Monitor import Page_Monitor
from demo_source import DemoSource

SIDEBAR_WIDTH = 190
STATUS_BAR_HEIGHT = 30


class Window():
    def __init__(self, usb:USB_Device, data_process:Data_Process, operations:list, run_time:dict, robot_cmd:dict) -> None:
        self.usb = usb
        self.data_process = data_process
        self.operations = operations
        self.run_time = run_time
        self.robot_cmd = robot_cmd

        self.window = tk.Tk()
        theme.apply(self.window)
        LogInfo("窗口已创建")
        self.version = 'V3.0.5'
        LogInfo('版本已确认：' + self.version)
        self.height = 0
        self.width = 0

        self.page_main = Page_Main(self.window,
                                   usb=self.usb, 
                                   data_process=self.data_process,
                                   operations=self.operations)
        self.page_debug = Page_Debug(self.window, self.data_process, self.usb)
        self.page_robot_cmd = Page_Robot_Cmd(self.window,
                                             self.robot_cmd,
                                             self.data_process)
        self.page_monitor = Page_Monitor(self.window, self.data_process, self.usb)
        self.page_log = Page_Log(self.window)
        self.all_pages = [self.page_main, self.page_debug,
                          self.page_robot_cmd, self.page_monitor, self.page_log]

        # 日志接入界面
        set_sink(self.page_log.append_log)

        # 演示数据源
        self.demo_source = DemoSource(self.data_process)

        # 状态栏速率统计
        self.start_time = time.time()
        self.last_stat_time = time.time()
        self.last_frames = 0
        self.last_errors = 0
        self.last_tx = 0
        self.last_rx_bytes = 0
        self.last_conn_state = None

        start_time = int(time.time() * 1000)
        self.run_time['TASK_Window'] = start_time
        LogInfo(f"[{start_time}(ms)]开始运行 StandardRobot++ 上位机的可视化模块")
        self.window.protocol("WM_DELETE_WINDOW", self.OnClose)
        self.FeedDog()
        return
    
    def BlankFunction(self):
        '''空函数，用于占位'''
        pass
    
    def FeedDog(self):
        self.run_time['TASK_Window'] = int(time.time() * 1000)
        # 看门狗只记录日志, 不再弹窗/退出, 保证界面始终可用
        self.window.after(300, self.FeedDog)
        return

    def OnClose(self):
        '''关闭窗口时清理资源'''
        try:
            self.demo_source.stop()
        except Exception:
            pass
        try:
            if self.usb.is_open:
                self.usb.close()
        except Exception:
            pass
        self.window.destroy()
        return

    ############################################################
    #  主要功能
    #  InitApp 初始化程序
    #  RunApp 运行程序
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

    ############################################################
    #  切换界面
    #  SwitchPage 切换界面
    ############################################################
    
    def SwitchPage(self, page_id:int):
        for page in self.all_pages:
            page.is_active = (page.id == page_id)

        # 更新侧边栏高亮
        for pid, button in self.nav_buttons.items():
            if pid == page_id:
                button.configure(bg=theme.CARD_HI, fg=theme.FG)
            else:
                button.configure(bg=theme.CARD, fg=theme.FG_DIM)

        # 左侧高亮条
        for pid, button in self.nav_buttons.items():
            if pid == page_id:
                self.active_marker.place(x=0, y=button.winfo_y() + 8,
                                         width=4, height=24)
                break

        # 机体控制页自动开始发送，其他页面停止发送
        if page_id == self.page_robot_cmd.id:
            self.data_process.start_send()
        else:
            self.data_process.stop_send()

        for page in self.all_pages:
            if page.id == page_id:
                page.lift()

    ############################################################
    #  界面创建
    #  InitUI 初始化UI
    #  CreateSidebar 创建侧边栏
    #  CreateStatusBar 创建状态栏
    #  CreatePages 创建页面
    ############################################################
    
    def InitUI(self):
        '''初始化UI'''
        self.window.title('StandardRobot++ Tool  ' + self.version)
        self.window.geometry(f'{self.width}x{self.height}+120+40')
        self.window.resizable(0,0)
        self.CreateSidebar()
        self.CreateStatusBar()
        self.CreatePages()
        self.CreateShortcuts()
        self.UpdateStatusBar()

    def CreateSidebar(self):
        '''左侧边栏'''
        bar = tk.Frame(self.window, bg=theme.CARD)
        bar.place(x=0, y=0, width=SIDEBAR_WIDTH, height=self.height)

        tk.Label(bar, text="StandardRobot++", bg=theme.CARD, fg=theme.FG,
                 font=(theme.FONT, 12, "bold")).place(x=16, y=18)
        tk.Label(bar, text="北极熊电控调试工具", bg=theme.CARD, fg=theme.FG_DIM,
                 font=theme.FONT_SM).place(x=16, y=44)
        tk.Frame(bar, bg=theme.BORDER, height=1).place(x=12, y=78,
                                                       width=SIDEBAR_WIDTH-24, height=1)

        self.nav_buttons = {}
        self.active_marker = tk.Frame(bar, bg=theme.ACCENT, width=4)
        items = [(self.page_main.id, "  主界面"),
                 (self.page_debug.id, "  调试数据"),
                 (self.page_robot_cmd.id, "  机体控制"),
                 (self.page_monitor.id, "  通信监控"),
                 (self.page_log.id, "  运行日志")]
        y = 94
        for page_id, text in items:
            btn = tk.Button(bar, text=text, anchor="w", relief="flat", bd=0,
                            padx=18, font=(theme.FONT, 11),
                            bg=theme.CARD, fg=theme.FG_DIM,
                            activebackground=theme.CARD_HI,
                            activeforeground=theme.FG,
                            cursor="hand2", highlightthickness=0,
                            command=lambda pid=page_id: self.SwitchPage(pid))
            btn.place(x=12, y=y, width=SIDEBAR_WIDTH-24, height=40)
            self.nav_buttons[page_id] = btn
            y += 46

        # 演示模式开关
        self.demo_button = theme.button(bar, text="演示数据：关",
                                        command=self.ToggleDemo)
        self.demo_button.place(x=16, y=self.height-160,
                               width=SIDEBAR_WIDTH-32, height=38)

        # 连接状态
        self.side_dot = tk.Canvas(bar, width=16, height=16, bg=theme.CARD,
                                  highlightthickness=0)
        self.side_dot.place(x=18, y=self.height-104)
        self.side_dot_item = self.side_dot.create_oval(3, 3, 13, 13,
                                                       fill=theme.ERR, outline="")
        self.side_state_label = theme.label(bar, "未连接", dim=True)
        self.side_state_label.place(x=42, y=self.height-104)

        tk.Label(bar, text="V3.0.5  ·  Dark UI", bg=theme.CARD, fg=theme.FG_DIM,
                 font=theme.FONT_SM).place(x=16, y=self.height-46)
        return

    def CreateStatusBar(self):
        '''底部状态栏'''
        bar = tk.Frame(self.window, bg=theme.CARD)
        bar.place(x=SIDEBAR_WIDTH, y=self.height-STATUS_BAR_HEIGHT,
                  width=self.width-SIDEBAR_WIDTH, height=STATUS_BAR_HEIGHT)

        self.status_conn = theme.label(bar, "未连接", dim=True, font=theme.FONT_SM)
        self.status_conn.place(x=14, y=6)

        self.status_rx = theme.label(bar, "RX      0 帧/s ·     0.0 KB/s",
                                     dim=True, font=theme.FONT_SM)
        self.status_rx.place(x=170, y=6)

        self.status_tx = theme.label(bar, "TX    0 包/s", dim=True, font=theme.FONT_SM)
        self.status_tx.place(x=400, y=6)

        self.status_err = theme.label(bar, "错误 0", dim=True, font=theme.FONT_SM)
        self.status_err.place(x=530, y=6)

        self.status_uptime = theme.label(bar, "运行 00:00:00", dim=True,
                                         font=theme.FONT_SM)
        self.status_uptime.place(x=self.width-SIDEBAR_WIDTH-130, y=6)
        return

    def CreatePages(self):
        '''创建页面'''
        page_width = self.width - SIDEBAR_WIDTH
        page_height = self.height - STATUS_BAR_HEIGHT

        for page in self.all_pages:
            if hasattr(page, 'CreatePage'):
                try:
                    page.CreatePage(page_width, page_height)
                except TypeError:
                    page.CreatePage()
            page.place(x=SIDEBAR_WIDTH, y=0, width=page_width, height=page_height)

        self.SwitchPage(self.page_main.id)

    def CreateShortcuts(self):
        '''快捷键'''
        self.window.bind("<F1>", lambda e: self.SwitchPage(self.page_main.id))
        self.window.bind("<F2>", lambda e: self.SwitchPage(self.page_debug.id))
        self.window.bind("<F3>", lambda e: self.SwitchPage(self.page_robot_cmd.id))
        self.window.bind("<F4>", lambda e: self.SwitchPage(self.page_monitor.id))
        self.window.bind("<F5>", lambda e: self.SwitchPage(self.page_log.id))
        self.window.bind("<F6>", lambda e: self.ToggleDemo())
        return

    ############################################################
    #  演示模式 & 状态栏
    ############################################################
    def ToggleDemo(self):
        running = self.demo_source.toggle()
        self.demo_button.configure(text="演示数据：开" if running else "演示数据：关")
        return

    def UpdateStatusBar(self):
        now = time.time()
        dt = now - self.last_stat_time
        if dt >= 0.4:
            stats = self.data_process.stats
            frames = stats['rx_frames'] - self.last_frames
            errors = stats['rx_errors'] - self.last_errors
            tx = stats['tx_packets'] - self.last_tx
            rx_bytes = self.usb.rx_bytes - self.last_rx_bytes

            self.last_frames = stats['rx_frames']
            self.last_errors = stats['rx_errors']
            self.last_tx = stats['tx_packets']
            self.last_rx_bytes = self.usb.rx_bytes
            self.last_stat_time = now

            demo_tag = "  ·  演示中" if stats['demo'] else ""
            replay_tag = "  ·  回放中" if stats.get('replaying') else ""
            self.status_rx.config(
                text=f"RX {frames/dt:5.0f} 帧/s · {rx_bytes/dt/1024:6.1f} KB/s{demo_tag}{replay_tag}")
            self.status_tx.config(text=f"TX {tx/dt:5.0f} 包/s")
            self.status_err.config(text=f"错误 {stats['rx_errors']}")

            uptime = int(now - self.start_time)
            self.status_uptime.config(
                text=f"运行 {uptime//3600:02d}:{uptime%3600//60:02d}:{uptime%60:02d}")

        # 连接状态
        conn_state = (self.usb.is_open, self.usb.port)
        if conn_state != self.last_conn_state:
            self.last_conn_state = conn_state
            if self.usb.is_open:
                # 连接真实设备后自动关闭演示数据，避免真假数据混在一起
                if self.demo_source.running:
                    self.demo_source.stop()
                    self.demo_button.configure(text="演示数据：关")
                    LogWarning("检测到串口已连接，已自动关闭演示数据")
                self.side_dot.itemconfigure(self.side_dot_item, fill=theme.OK)
                self.side_state_label.config(text=f"已连接 {self.usb.port}",
                                             fg=theme.FG)
                self.status_conn.config(text=f"已连接 {self.usb.port}", fg=theme.FG)
            else:
                self.side_dot.itemconfigure(self.side_dot_item, fill=theme.ERR)
                self.side_state_label.config(text="未连接", fg=theme.FG_DIM)
                self.status_conn.config(text="未连接", fg=theme.FG_DIM)

        self.window.after(400, self.UpdateStatusBar)
        return

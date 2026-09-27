import csv
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

import theme
from CustomWidget import DataNameModel, PlotGraphModel
from lib.data_procecss import Data_Process
from lib.log_info import LogInfo, LogWarning

PLOT_MAX_POINTS = 2000

class Page_Debug(tk.Frame):
    def __init__(self, master, data_process:Data_Process, usb=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.configure(bg=theme.BG)
        self.id = 2
        self.is_active = False
        self.data_process = data_process
        self.usb = usb
        self.is_ploting = False
        self.is_paused = False
        self.window_sec = 10.0
        self.auto_selected = False
        self._replay_button_state = False
        self._last_draw_sig = None
        self.recorded_frames = []
        self.data_name_moodel = DataNameModel(self)
        self.plot_graph_model = PlotGraphModel(self)
        self.after(10, self.UpdateDataNameList) # 10ms后更新数据名称列表
        self.after(10, self.UpdatePlot) # 10ms后更新数据名称列表
    
    def CreatePage(self,width:int,height:int) -> None:
        # 工具栏
        self.status_dot = tk.Canvas(self, width=18, height=18, bg=theme.BG,
                                    highlightthickness=0)
        self.status_dot.place(x=16, y=24)
        self.dot_item = self.status_dot.create_oval(3, 3, 15, 15,
                                                    fill=theme.ERR, outline="")

        self.button_toggle_Port = theme.button(self, text='开始绘图',
                                               command=self.TogglePlot)
        self.button_toggle_Port.place(x=42, y=14, width=110, height=38)

        self.button_pause = theme.button(self, text='暂停', command=self.TogglePause)
        self.button_pause.place(x=160, y=14, width=90, height=38)

        self.button_clear = theme.button(self, text='清空', command=self.ClearData)
        self.button_clear.place(x=258, y=14, width=90, height=38)

        theme.label(self, "时间窗", dim=True, bg=theme.BG).place(x=366, y=26)
        self.combobox_window = ttk.Combobox(self, values=['5 s', '10 s', '30 s', '全部'],
                                            state='readonly', width=6,
                                            font=theme.FONT_TXT,
                                            style="Dark.TCombobox")
        self.combobox_window.current(1)
        self.combobox_window.place(x=418, y=18, width=90, height=30)
        self.combobox_window.bind('<<ComboboxSelected>>', self.OnWindowChanged)

        self.button_csv = theme.button(self, text='导出 CSV', command=self.ExportCsv)
        self.button_csv.place(x=526, y=14, width=110, height=38)

        self.button_png = theme.button(self, text='导出图片', command=self.ExportPng)
        self.button_png.place(x=644, y=14, width=110, height=38)

        # 左边为数据名称列表，右边为绘图区域
        self.data_name_moodel.place(x=16, y=66, width=250, height=height-190)
        self.plot_graph_model.place(x=282, y=14, width=width-298, height=height-28)

        # 录制/回放面板
        card = theme.card(self, "录制 / 回放")
        card.place(x=16, y=height-116, width=250, height=100)
        self.button_record = theme.button(card, text='开始录制', command=self.ToggleRecord)
        self.button_record.place(x=12, y=16, width=105, height=32)
        self.button_save = theme.button(card, text='保存录制', command=self.SaveRecord)
        self.button_save.place(x=133, y=16, width=105, height=32)
        self.button_replay = theme.button(card, text='回放', command=self.ToggleReplay)
        self.button_replay.place(x=12, y=56, width=105, height=32)
        self.combobox_speed = ttk.Combobox(card, values=['0.5x', '1x', '2x', '4x'],
                                           state='readonly', width=6,
                                           font=theme.FONT_TXT, style="Dark.TCombobox")
        self.combobox_speed.current(1)
        self.combobox_speed.place(x=133, y=58, width=105, height=28)
        self.combobox_speed.bind('<<ComboboxSelected>>', self.OnSpeedChanged)
        return

    ############################################################
    #  实时任务
    #  UpdateDataNameList 更新数据名称列表
    #  UpdatePlot 更新绘图
    ############################################################
    
    def UpdateDataNameList(self) -> None:
        '''更新数据名称列表'''
        data_name_list = list(self.data_process.debug_data.latest['datas'].keys())
        self.data_name_moodel.UpdateDataNameList(data_name_list)
        self.data_name_moodel.UpdateCheckbuttons()

        # 首次收到数据时默认勾选第一个变量，方便直接看到波形
        if (not self.auto_selected) and len(data_name_list) > 0:
            self.auto_selected = True
            if (not self.data_name_moodel.selected_names) and self.data_name_moodel.list_Checkbuttons:
                self.data_name_moodel.list_Checkbuttons[0][0].invoke()

        self.after(500, self.UpdateDataNameList) # 500ms后更新数据名称列表
        return
    
    def UpdatePlot(self) -> None:
        # 回放状态同步到按钮
        if self._replay_button_state != self.data_process.replaying:
            self._replay_button_state = self.data_process.replaying
            self.button_replay.configure(
                text='停止回放' if self._replay_button_state else '回放')

        if self.is_ploting and self.is_active and not self.is_paused:
            storage = self.data_process.debug_data.storage
            names = [n for n in self.data_name_moodel.selected_names
                     if n in storage['datas']]

            # 数据无变化时跳过重绘(静止时几乎不耗CPU)
            time_stamp_all = storage['time_stamp']
            signature = (tuple(names), len(time_stamp_all),
                         time_stamp_all[-1] if time_stamp_all else None,
                         self.window_sec)
            if signature == self._last_draw_sig:
                self.after(100, self.UpdatePlot)
                return
            self._last_draw_sig = signature

            if len(names) == 0:
                self.plot_graph_model.UpdateGraph([], [[]], [])
            else:
                series = [storage['datas'][name][-PLOT_MAX_POINTS:] for name in names]
                time_stamp = storage['time_stamp'][-PLOT_MAX_POINTS:]
                n = min([len(time_stamp)] + [len(s) for s in series])
                if n == 0:
                    self.plot_graph_model.UpdateGraph([], [[]], [])
                else:
                    time_stamp = time_stamp[-n:]
                    series = [s[-n:] for s in series]

                    # 时间窗口裁剪
                    if self.window_sec is not None and n > 1:
                        t_end = time_stamp[-1]
                        start = 0
                        for i in range(n - 1, -1, -1):
                            if t_end - time_stamp[i] > self.window_sec:
                                start = i + 1
                                break
                        time_stamp = time_stamp[start:]
                        series = [s[start:] for s in series]

                    self.plot_graph_model.UpdateGraph(time_stamp, series, names)

        # 不在前台或未绘图时降低刷新率
        interval = 33 if (self.is_active and self.is_ploting and not self.is_paused) else 200
        self.after(interval, self.UpdatePlot) # 33ms(约30FPS)更新图片
        return
    ############################################################
    #  回调函数
    #  TogglePlot 变更绘图状态
    #  TogglePause 暂停/继续
    #  ClearData 清空数据
    #  ExportCsv / ExportPng 导出
    ############################################################
    
    def TogglePlot(self) -> None:
        self.is_ploting = not self.is_ploting
        self._last_draw_sig = None
        if self.is_ploting:
            self.status_dot.itemconfigure(self.dot_item, fill=theme.OK)
            self.button_toggle_Port.configure(text='停止绘图')
        else:
            self.status_dot.itemconfigure(self.dot_item, fill=theme.ERR)
            self.button_toggle_Port.configure(text='开始绘图')
        return

    def TogglePause(self) -> None:
        self.is_paused = not self.is_paused
        self.button_pause.configure(text='继续' if self.is_paused else '暂停')
        LogInfo("波形显示已暂停" if self.is_paused else "波形显示已继续")
        return

    def ClearData(self) -> None:
        self.data_process.debug_data.clear()
        self._last_draw_sig = None
        self.plot_graph_model.UpdateGraph([], [[]], [])
        LogInfo("调试数据已清空")
        return

    def OnWindowChanged(self, event=None) -> None:
        mapping = {'5 s': 5.0, '10 s': 10.0, '30 s': 30.0, '全部': None}
        self.window_sec = mapping.get(self.combobox_window.get(), 10.0)
        return

    def ToggleRecord(self) -> None:
        if self.data_process.recording:
            self.data_process.stop_record()
            self.button_record.configure(text='开始录制')
        else:
            self.data_process.start_record()
            self.button_record.configure(text='停止录制')
        return

    def SaveRecord(self) -> None:
        if not self.data_process.recorded:
            LogWarning("还没有录制数据，请先点击“开始录制”")
            return
        path = filedialog.asksaveasfilename(
            title="保存录制数据",
            defaultextension=".pbr",
            filetypes=[("录制文件", "*.pbr")])
        if not path:
            return
        self.data_process.save_record(path)
        return

    def ToggleReplay(self) -> None:
        if self.data_process.replaying:
            self.data_process.stop_replay()
            return
        if (self.usb is not None) and self.usb.is_open:
            LogWarning("请先关闭串口再回放数据")
            return
        path = filedialog.askopenfilename(
            title="选择回放文件",
            filetypes=[("录制文件", "*.pbr"), ("所有文件", "*.*")])
        if not path:
            return
        frames = self.data_process.load_record(path)
        if frames:
            self.data_process.start_replay(frames)
        return

    def OnSpeedChanged(self, event=None) -> None:
        try:
            self.data_process.replay_speed = float(self.combobox_speed.get()[:-1])
            LogInfo(f"回放速度已设置为 {self.combobox_speed.get()}")
        except Exception:
            pass
        return

    def ExportCsv(self) -> None:
        path = filedialog.asksaveasfilename(
            title="保存调试数据",
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv")])
        if not path:
            return
        storage = self.data_process.debug_data.storage
        names = list(storage['datas'].keys())
        time_stamp = storage['time_stamp']
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['time(s)'] + names)
            for i in range(len(time_stamp)):
                row = [f"{time_stamp[i]:.4f}"]
                for name in names:
                    data = storage['datas'][name]
                    row.append(f"{data[i]:.6f}" if i < len(data) else '')
                writer.writerow(row)
        LogInfo(f"调试数据已导出: {path}")
        return

    def ExportPng(self) -> None:
        path = filedialog.asksaveasfilename(
            title="保存波形图片",
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png")])
        if not path:
            return
        self.plot_graph_model.ExportImage(path)
        LogInfo(f"波形图片已导出: {path}")
        return

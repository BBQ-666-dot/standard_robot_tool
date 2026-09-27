
import bisect
import math
import tkinter as tk

import theme
from lib.log_info import LogError , LogInfo , LogWarning


# 旋转矩阵（绕X轴旋转theta角度）
def rotate_x(points, theta):
    c, s = math.cos(theta), math.sin(theta)
    return (points[0],
            c * points[1] - s * points[2],
            s * points[1] + c * points[2])

# 旋转矩阵（绕Y轴旋转theta角度）
def rotate_y(points, theta):
    c, s = math.cos(theta), math.sin(theta)
    return (c * points[0] + s * points[2],
            points[1],
            -s * points[0] + c * points[2])

# 旋转矩阵（绕Z轴旋转theta角度）
def rotate_z(points, theta):
    c, s = math.cos(theta), math.sin(theta)
    return (c * points[0] - s * points[1],
            s * points[0] + c * points[1],
            points[2])


class PlotGraphModel(tk.Frame):
    '''波形绘制模块(Tk Canvas实现, 高帧率)'''

    MARGIN_L = 64
    MARGIN_R = 20
    MARGIN_T = 68
    MARGIN_B = 44

    def __init__(self, master=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.configure(bg=theme.CARD, highlightthickness=1,
                       highlightbackground=theme.BORDER)
        self.canvas = tk.Canvas(self, bg=theme.CARD, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.area = (self.MARGIN_L, self.MARGIN_T, 700, 480)
        self._lines = []
        self._legend_items = []
        self._grid_items = []
        self._y_label_items = []
        self._x_label_items = []
        self._empty_text = None
        self._last_data = ([], [[]], [])
        self._map = None
        self._cursor_line = None
        self._cursor_text = None
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<Leave>", self._on_leave)
        return

    ############################################################
    #  布局与静态元素
    ############################################################
    def _on_resize(self, event):
        w, h = event.width, event.height
        self.area = (self.MARGIN_L, self.MARGIN_T,
                     max(self.MARGIN_L + 10, w - self.MARGIN_R),
                     max(self.MARGIN_T + 10, h - self.MARGIN_B))
        self._draw_grid()
        self._empty_text = None
        # 重绘空态(显示提示与标题)
        self.UpdateGraph([], [[]], [])
        return

    def _draw_grid(self):
        c = self.canvas
        # 删除旧的空态提示(避免resize后残留)
        if self._empty_text is not None:
            c.delete(self._empty_text)
            self._empty_text = None
        for item in self._grid_items:
            c.delete(item)
        self._grid_items = []
        for item in self._y_label_items + self._x_label_items:
            c.delete(item)
        self._y_label_items = []
        self._x_label_items = []

        l, t, r, b = self.area
        # 标题与坐标轴名称(标题放在工具栏下方避免被遮)
        self._grid_items.append(
            c.create_text(l, 44, text="调试波形 Debug Waveform", anchor="w",
                          fill=theme.FG_DIM, font=(theme.FONT, 10, "bold")))
        self._grid_items.append(
            c.create_text(l - 48, (t + b) / 2, text="value", angle=90,
                          fill=theme.FG_DIM, font=(theme.FONT, 9)))
        self._grid_items.append(
            c.create_text((l + r) / 2, b + 32, text="time (s)",
                          fill=theme.FG_DIM, font=(theme.FONT, 9)))

        for i in range(6):
            x = l + (r - l) * i / 5.0
            y = t + (b - t) * i / 5.0
            self._grid_items.append(c.create_line(x, t, x, b, fill=theme.BORDER))
            self._grid_items.append(c.create_line(l, y, r, y, fill=theme.BORDER))
            self._y_label_items.append(c.create_text(l - 8, y, text="", anchor="e",
                                                     fill=theme.FG_DIM, font=(theme.FONT, 8)))
            self._x_label_items.append(c.create_text(x, b + 16, text="", anchor="n",
                                                     fill=theme.FG_DIM, font=(theme.FONT, 8)))
        return

    def _update_axis_labels(self, y_range, x_range):
        l, t, r, b = self.area
        if y_range is None:
            for item in self._y_label_items:
                self.canvas.itemconfigure(item, text="")
            for item in self._x_label_items:
                self.canvas.itemconfigure(item, text="")
            return
        ymin, ymax = y_range
        for i, item in enumerate(self._y_label_items):
            value = ymax - (ymax - ymin) * i / 5.0
            self.canvas.itemconfigure(item, text=f"{value:.2f}")
        x0, x1 = x_range
        for i, item in enumerate(self._x_label_items):
            value = x0 + (x1 - x0) * i / 5.0
            self.canvas.itemconfigure(item, text=f"{value:.1f}")
        return

    def _update_legend(self, labels):
        c = self.canvas
        l, t, r, b = self.area
        while len(self._legend_items) < len(labels):
            self._legend_items.append(
                c.create_text(0, 0, anchor="ne", font=(theme.FONT, 9)))
        for i, item in enumerate(self._legend_items):
            if i < len(labels):
                color = theme.LINE_COLORS[i % len(theme.LINE_COLORS)]
                c.coords(item, r - 6, t + 4 + i * 18)
                c.itemconfigure(item, text=labels[i], fill=color, state="normal")
            else:
                c.itemconfigure(item, state="hidden")
        return

    ############################################################
    #  波形光标(十字线+数值读数)
    ############################################################
    def _hide_cursor(self):
        for item in (self._cursor_line, self._cursor_text):
            if item is not None:
                self.canvas.itemconfigure(item, state="hidden")
        return

    def _on_leave(self, event=None):
        self._hide_cursor()
        return

    def _on_motion(self, event):
        if self._map is None or not self._last_data[0]:
            return
        l, t, r, b = self.area
        if event.x < l or event.x > r or event.y < t or event.y > b:
            self._hide_cursor()
            return

        x0, x1, ymin, ymax = self._map
        x_data, ys, labels = self._last_data
        n = len(x_data)
        t_value = x0 + (event.x - l) / max(1.0, (r - l)) * (x1 - x0)

        i = bisect.bisect_left(x_data, t_value)
        if i <= 0:
            idx = 0
        elif i >= n:
            idx = n - 1
        else:
            idx = i if abs(x_data[i] - t_value) < abs(x_data[i - 1] - t_value) else i - 1

        px = l + (x_data[idx] - x0) / max(1e-9, (x1 - x0)) * (r - l)
        if self._cursor_line is None:
            self._cursor_line = self.canvas.create_line(0, t, 0, b,
                                                        fill=theme.FG_DIM, dash=(3, 3))
        self.canvas.coords(self._cursor_line, px, t, px, b)
        self.canvas.itemconfigure(self._cursor_line, state="normal")

        lines = [f"t = {x_data[idx]:.3f}s"]
        for i2, series in enumerate(ys):
            if idx < len(series):
                name = labels[i2] if i2 < len(labels) else f"ch{i2}"
                lines.append(f"{name} = {series[idx]:.4g}")
        text = "\n".join(lines)
        if self._cursor_text is None:
            self._cursor_text = self.canvas.create_text(0, 0, anchor="nw",
                                                        fill=theme.FG,
                                                        font=(theme.FONT, 9),
                                                        justify="left")
        if px + 230 < r:
            tx, anchor = px + 10, "nw"
        else:
            tx, anchor = px - 10, "ne"
        self.canvas.itemconfigure(self._cursor_text, text=text,
                                  anchor=anchor, state="normal")
        self.canvas.coords(self._cursor_text, tx, t + 4)
        return

    ############################################################
    #  主要功能
    #  UpdateGraph 更新图像(保持与原接口一致)
    #  ExportImage 用matplotlib渲染当前数据保存图片
    ############################################################
    def UpdateGraph(self, x_axis_data:list, y_axis_data:list, y_labels:list) -> None:
        c = self.canvas
        self._last_data = (list(x_axis_data),
                           [list(y) for y in y_axis_data],
                           list(y_labels))

        valid = [y for y in y_axis_data if len(y) > 0] if y_axis_data else []
        l, t, r, b = self.area

        if len(x_axis_data) == 0 or len(valid) == 0:
            for item in self._lines:
                c.itemconfigure(item, state="hidden")
            self._map = None
            self._hide_cursor()
            mid_x, mid_y = (l + r) / 2.0, (t + b) / 2.0
            if self._empty_text is None:
                self._empty_text = c.create_text(mid_x, mid_y,
                                                 text="等待数据 / Waiting for data",
                                                 fill=theme.FG_DIM,
                                                 font=(theme.FONT, 12))
            else:
                c.coords(self._empty_text, mid_x, mid_y)
                c.itemconfigure(self._empty_text, state="normal")
            self._update_axis_labels(None, None)
            self._update_legend([])
            return

        if self._empty_text is not None:
            c.itemconfigure(self._empty_text, state="hidden")

        ymin = min(min(y) for y in valid)
        ymax = max(max(y) for y in valid)
        if ymax - ymin < 1e-9:
            ymin -= 1.0
            ymax += 1.0
        pad = (ymax - ymin) * 0.08
        ymin -= pad
        ymax += pad

        x0, x1 = x_axis_data[0], x_axis_data[-1]
        if abs(x1 - x0) < 1e-9:
            x1 = x0 + 1e-3
        self._map = (x0, x1, ymin, ymax)

        span_x = x1 - x0
        span_y = ymax - ymin
        width = r - l
        height = b - t
        n_x = len(x_axis_data)

        while len(self._lines) < len(y_axis_data):
            self._lines.append(c.create_line(0, 0, 0, 0, width=2,
                                             joinstyle=tk.ROUND, capstyle=tk.ROUND))

        for i, series in enumerate(y_axis_data):
            item = self._lines[i]
            if len(series) < 2:
                c.itemconfigure(item, state="hidden")
                continue
            step = max(1, len(series) // 900)
            coords = []
            for j in range(0, len(series), step):
                xj = x_axis_data[j] if j < n_x else x_axis_data[-1]
                coords.append(l + (xj - x0) / span_x * width)
                coords.append(b - (series[j] - ymin) / span_y * height)
            c.coords(item, *coords)
            c.itemconfigure(item, state="normal",
                            fill=theme.LINE_COLORS[i % len(theme.LINE_COLORS)])

        for i in range(len(y_axis_data), len(self._lines)):
            c.itemconfigure(self._lines[i], state="hidden")

        self._update_axis_labels((ymin, ymax), (x0, x1))
        self._update_legend(y_labels)
        return

    def ExportImage(self, path:str) -> None:
        '''用matplotlib把当前数据渲染成图片(仅导出时用, 不影响实时性能)'''
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False

        x, ys, labels = self._last_data
        fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
        ax.set_facecolor(theme.CARD)
        fig.patch.set_facecolor(theme.CARD)
        if len(x) > 0:
            for i, series in enumerate(ys):
                if len(series) == 0:
                    continue
                n = min(len(series), len(x))
                ax.plot(x[-n:], series[-n:], linewidth=1.4,
                        label=labels[i] if i < len(labels) else '',
                        color=theme.LINE_COLORS[i % len(theme.LINE_COLORS)])
        for spine in ax.spines.values():
            spine.set_color(theme.BORDER)
        ax.tick_params(colors=theme.FG_DIM, labelsize=9)
        ax.grid(True, color=theme.BORDER, alpha=0.45, linewidth=0.6)
        ax.set_xlabel('time (s)', color=theme.FG_DIM, fontsize=10)
        ax.set_ylabel('value', color=theme.FG_DIM, fontsize=10)
        ax.set_title('调试波形 Debug Waveform', color=theme.FG, fontsize=11)
        if len(labels) > 0 and len(x) > 0:
            legend = ax.legend(loc='upper right', fontsize=9,
                               facecolor=theme.CARD_HI, edgecolor=theme.BORDER)
            for text in legend.get_texts():
                text.set_color(theme.FG)
        fig.subplots_adjust(left=0.10, right=0.98, top=0.92, bottom=0.12)
        fig.savefig(path, facecolor=fig.get_facecolor())
        plt.close(fig)
        return


class PostureGraphModel(tk.Frame):
    '''IMU 3D姿态显示(Tk Canvas实现, 高帧率)'''

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=theme.CARD, highlightthickness=1,
                       highlightbackground=theme.BORDER)
        self.canvas = tk.Canvas(self, bg=theme.CARD, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.cx = 200.0
        self.cy = 200.0
        self.scale = 120.0

        self.axis_items = {}
        self._build_axes()
        self.canvas.bind("<Configure>", self._on_resize)
        return

    ############################################################
    #  静态参考系与姿态轴
    ############################################################
    def _build_axes(self):
        colors = {"x": "#ff6b6b", "y": "#51cf66", "z": "#4dabf7"}
        for key in ("x", "y", "z"):
            line = self.canvas.create_line(0, 0, 0, 0, fill=colors[key],
                                           width=3, capstyle=tk.ROUND)
            head = self.canvas.create_polygon(0, 0, 0, 0, 0, 0,
                                              fill=colors[key], outline="")
            text = self.canvas.create_text(0, 0, text=key.upper(),
                                           fill=colors[key],
                                           font=(theme.FONT, 10, "bold"))
            self.axis_items[key] = (line, head, text)
        return

    def _on_resize(self, event):
        self.cx = event.width / 2.0
        self.cy = event.height / 2.0
        self.scale = min(event.width, event.height) * 0.34
        self._draw_reference()
        return

    def _proj(self, x, y, z):
        '''固定相机投影: 世界坐标 -> 画布坐标'''
        sx = -0.50 * x + 0.87 * y
        sy = 0.32 * x + 0.32 * y - 0.85 * z
        return self.cx + sx * self.scale, self.cy + sy * self.scale

    def _draw_reference(self):
        c = self.canvas
        c.delete("reference")
        # 三个参考大圆
        for plane in range(3):
            pts = []
            for i in range(65):
                t = 2.0 * math.pi * i / 64.0
                if plane == 0:
                    p = (math.cos(t), math.sin(t), 0.0)
                elif plane == 1:
                    p = (math.cos(t), 0.0, math.sin(t))
                else:
                    p = (0.0, math.cos(t), math.sin(t))
                px, py = self._proj(*p)
                pts.append(px)
                pts.append(py)
            c.create_line(*pts, fill=theme.BORDER, width=1, tags="reference")
        # 世界参考轴(虚线)
        for i in range(3):
            v = [0.0, 0.0, 0.0]
            v[i] = 1.28
            x0, y0 = self._proj(-v[0], -v[1], -v[2])
            x1, y1 = self._proj(v[0], v[1], v[2])
            c.create_line(x0, y0, x1, y1, fill="#39414f", width=1,
                          dash=(3, 3), tags="reference")
        c.tag_lower("reference")
        return

    ############################################################
    #  主要功能
    #  UpdateGraph 更新姿态(保持与原接口一致)
    ############################################################
    def UpdateGraph(self, thetas:dict) -> None:
        theta_x = thetas['roll']
        theta_y = thetas['pitch']
        theta_z = thetas['yaw']

        for key, base in (("x", (1.0, 0.0, 0.0)),
                          ("y", (0.0, 1.0, 0.0)),
                          ("z", (0.0, 0.0, 1.0))):
            v = rotate_x(base, theta_x)
            v = rotate_y(v, theta_y)
            v = rotate_z(v, theta_z)
            line, head, text = self.axis_items[key]
            self._set_axis(line, head, text, v)
        return

    def _set_axis(self, line, head, text, vec):
        c = self.canvas
        ox, oy = self._proj(0.0, 0.0, 0.0)
        px, py = self._proj(vec[0], vec[1], vec[2])
        dx, dy = px - ox, py - oy
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx / length, dy / length
        head_len = 13.0
        bx, by = px - ux * head_len, py - uy * head_len
        c.coords(line, ox, oy, bx, by)
        nx, ny = -uy, ux
        c.coords(head, px, py,
                 bx + nx * 5.5, by + ny * 5.5,
                 bx - nx * 5.5, by - ny * 5.5)
        c.coords(text, px + ux * 14.0, py + uy * 14.0)
        return


class DataNameModel(tk.Frame):
    '''数据名称列表'''
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=theme.CARD, highlightthickness=1,
                       highlightbackground=theme.BORDER)
        self.list_Checkbuttons = [] #存储Checkbutton的列表：[(Checkbutton, IntVar),...]，其中IntVar为Checkbutton的状态
        self.name_list = [] #存储数据名称的列表
        self.selected_names = [] #存储被选中的数据名称
        self.name_list_is_updated = False #数据名称列表是否更新
        self.AddWidget()

    def AddWidget(self):
        # 创建label提示内容
        self.label = theme.label(self, "数据变量", dim=True, anchor="w")
        self.label.pack(side="top", fill="x", padx=12, pady=(8, 4))
        # 创建一个Canvas和一个Scrollbar
        box = tk.Frame(self, bg=theme.CARD)
        box.pack(side="top", fill="both", expand=True, padx=8, pady=(0, 8))
        self.canvas = tk.Canvas(box, bg=theme.CARD, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(box, orient="vertical", command=self.canvas.yview,
                                      bg=theme.CARD_HI, troughcolor=theme.CARD,
                                      activebackground=theme.BORDER, bd=0,
                                      relief="flat", width=12,
                                      elementborderwidth=0,
                                      highlightthickness=0,
                                      highlightbackground=theme.CARD)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        # 创建一个Frame来包含所有的Checkbutton
        self.frame = tk.Frame(self.canvas, bg=theme.CARD)
        self.canvas.create_window((0,0), window=self.frame, anchor='nw')
        # 当Frame的大小改变时，更新Canvas的滚动区域
        self.frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # 绑定鼠标滚轮事件
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def UpdateDataNameList(self, name_list:list):
        '''
        更新数据名称列表
        name_list:数据名称列表
        '''
        self.name_list = name_list.copy()

    def UpdateCheckbuttons(self):
        for i,name in enumerate(self.name_list):
            if i<self.list_Checkbuttons.__len__():
                self.ChangeCheckbutton(name, i)
            else:
                self.AddCheckbutton(name)
        for i in range(self.name_list.__len__(),self.list_Checkbuttons.__len__()):
            self.RemoveCheckbutton(i)


    def AddCheckbutton(self, text:str):
        '''
        添加Checkbutton
        text:Checkbutton的文本
        '''
        var = tk.IntVar()
        var.set(0)
        checkbutton = tk.Checkbutton(self.frame, text=text, variable=var,
                                     font=theme.FONT_TXT,
                                     bg=theme.CARD, fg=theme.FG,
                                     activebackground=theme.CARD,
                                     activeforeground=theme.FG,
                                     selectcolor=theme.CARD_HI,
                                     highlightthickness=0, bd=0, anchor="w",
                                     command=lambda:self.SelectedNamesUpdate(text,var.get()))
        self.list_Checkbuttons.append((checkbutton, var))
        checkbutton.pack(fill="x", padx=8, anchor="w")


    def ChangeCheckbutton(self, text:str, index:int):
        '''
        修改Checkbutton的文本
        text:Checkbutton的文本
        index:Checkbutton的索引
        '''
        checkbutton, var = self.list_Checkbuttons[index]
        original_text = checkbutton.cget('text')
        if original_text == text:
            return
        if var.get():
            self.selected_names.remove(original_text)
        var.set(0)
        checkbutton.config(text=text)
        checkbutton.config(command=lambda:self.SelectedNamesUpdate(text,var.get()))


    def RemoveCheckbutton(self, index:int):
        '''
        删除Checkbutton
        index:Checkbutton的索引
        '''
        checkbutton, var = self.list_Checkbuttons[index]
        if var.get():
            self.selected_names.remove(checkbutton.cget('text'))
        self.list_Checkbuttons[index][0].destroy()


    def Clear(self):
        '''
        清空Checkbutton
        '''
        for item in self.list_Checkbuttons:
            item[0].destroy()
        self.list_Checkbuttons.clear()
        self.name_list.clear()


    def SelectedNamesUpdate(self,name:str,select:int):
        '''
        更新被选中的数据名称
        name:数据名称
        '''
        if select and (name not in self.selected_names):
            self.selected_names.append(name)
        elif not select and (name in self.selected_names):
            self.selected_names.remove(name)
        self.CallUpdateNames(self.selected_names)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta//120), "units")


    def CallStartUpdatePlotGraph(self, names:list):
        pass


    def CallUpdateNames(self, name_list:list):
        pass


    def UpdateNameListCallback(self, name_list:list):
        self.name_list = name_list.copy()
        self.name_list_is_updated = True
        self.UpdateCheckbuttons()
        if self.selected_names.__len__() == 0:#如果没有被选中的数据名称，则默认选中第一个数据名称
            self.list_Checkbuttons[0][0].invoke()
        self.CallStartUpdatePlotGraph(self.selected_names)
        LogInfo(f"更新数据名称列表：{self.name_list}")


    def NotUpdateNameListCallback(self):
        self.name_list_is_updated = False

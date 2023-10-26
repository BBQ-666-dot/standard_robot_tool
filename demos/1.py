import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


class SinPlot:
    def __init__(self, master):
        self.master = master
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.draw()

        # 绘制初始正弦函数图像
        self.x = np.linspace(0, 2 * np.pi, 100)
        self.y = np.sin(self.x)
        self.ax.plot(self.x, self.y)

        # 添加鼠标事件处理
        self.canvas.mpl_connect("button_press_event", self.on_button_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion_notify)
        self.canvas.mpl_connect("button_release_event", self.on_button_release)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)

        # 右键拖动图像
        self.dragging = False
        self.last_x = 0
        self.last_y = 0

        # 中键缩放图像
        self.zoom_factor = 1.2

    def on_button_press(self, event):
        if event.button == 3:
            self.dragging = True
            self.last_x = event.x
            self.last_y = event.y

    def on_motion_notify(self, event):
        if self.dragging:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.ax.set_xlim(self.ax.get_xlim() - dx * 0.01)
            self.ax.set_ylim(self.ax.get_ylim() + dy * 0.01)
            self.canvas.draw()
            self.last_x = event.x
            self.last_y = event.y

    def on_button_release(self, event):
        if event.button == 3:
            self.dragging = False

    def on_scroll(self, event):
        if event.button == 'middle':
            if event.delta > 0:
                self.ax.set_xlim(self.ax.get_xlim() / self.zoom_factor)
                self.ax.set_ylim(self.ax.get_ylim() / self.zoom_factor)
            else:
                self.ax.set_xlim(self.ax.get_xlim() * self.zoom_factor)
                self.ax.set_ylim(self.ax.get_ylim() * self.zoom_factor)
            self.canvas.draw()


class App:
    def __init__(self, master):
        self.master = master
        self.sin_plot = SinPlot(self.master)


root = tk.Tk()
app = App(root)
root.mainloop()

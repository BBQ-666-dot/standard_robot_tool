import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class RealTimePlot:
    def __init__(self, ax):
        self.ax = ax
        
        self.ax._button_pressed = False
        self.ax._button_press_event = None
        self.ax._dragging = False
        self.ax._drag_start = (0, 0)
        self.ax._zoom_scale = 1.0
        self.ax._move_position = (0, 0)
        
    def update_plot(self):
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x)
        
        self.ax.cla()
        self.ax.plot(x, y)
        
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_center = 0.5 * (xlim[0] + xlim[1]) + self.ax._move_position[0]
        y_center = 0.5 * (ylim[0] + ylim[1]) + self.ax._move_position[1]
        x_width = xlim[1] - xlim[0]
        y_width = ylim[1] - ylim[0]
        new_x_width = x_width * self.ax._zoom_scale
        new_y_width = y_width * self.ax._zoom_scale
        self.ax.set_xlim(x_center - 0.5 * new_x_width, x_center + 0.5 * new_x_width)
        self.ax.set_ylim(y_center - 0.5 * new_y_width, y_center + 0.5 * new_y_width)
    
    def on_button_press(self, event):
        if event.button == 1:
            self.ax._button_pressed = True
            self.ax._button_press_event = event
        elif event.button == 3:
            self.ax._dragging = True
            self.ax._drag_start = (event.x, event.y)
    
    def on_button_release(self, event):
        if event.button == 1:
            self.ax._button_pressed = False
        elif event.button == 3:
            self.ax._dragging = False
    
    def on_mouse_move(self, event):
        if self.ax._button_pressed:
            dx = event.x - self.ax._button_press_event.x
            dy = event.y - self.ax._button_press_event.y
            dx/=100000
            dy/=100000
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.ax._move_position = (self.ax._move_position[0] + dx, self.ax._move_position[1] + dy)
            x_center = 0.5 * (xlim[0] + xlim[1]) + self.ax._move_position[0]
            y_center = 0.5 * (ylim[0] + ylim[1]) + self.ax._move_position[1]
            x_width = xlim[1] - xlim[0]
            y_width = ylim[1] - ylim[0]
            new_x_width = x_width * self.ax._zoom_scale
            new_y_width = y_width * self.ax._zoom_scale
            self.ax.set_xlim(x_center - 0.5 * new_x_width, x_center + 0.5 * new_x_width)
            self.ax.set_ylim(y_center - 0.5 * new_y_width, y_center + 0.5 * new_y_width)
        elif self.ax._dragging:
            dx = event.x - self.ax._drag_start[0]
            dy = event.y - self.ax._drag_start[1]
            dx/=100000
            dy/=100000
            self.ax._drag_start = (event.x, event.y)
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.ax._move_position = (self.ax._move_position[0] + dx, self.ax._move_position[1] + dy)
            x_center = 0.5 * (xlim[0] + xlim[1]) + self.ax._move_position[0]
            y_center = 0.5 * (ylim[0] + ylim[1]) + self.ax._move_position[1]
            x_width = xlim[1] - xlim[0]
            y_width = ylim[1] - ylim[0]
            new_x_width = x_width * self.ax._zoom_scale
            new_y_width = y_width * self.ax._zoom_scale
            self.ax.set_xlim(x_center - 0.5 * new_x_width, x_center + 0.5 * new_x_width)
            self.ax.set_ylim(y_center - 0.5 * new_y_width, y_center + 0.5 * new_y_width)
        
        plt.draw()
    
    def on_mouse_scroll(self, event):
        if event.button == 'up':
            self.ax._zoom_scale *= 0.9
        elif event.button == 'down':
            self.ax._zoom_scale *= 1.1

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("实时2D折线图")
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.plot = RealTimePlot(self.ax)
        
        self.canvas.mpl_connect('button_press_event', self.plot.on_button_press)
        self.canvas.mpl_connect('button_release_event', self.plot.on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self.plot.on_mouse_move)
        self.canvas.mpl_connect('scroll_event', self.plot.on_mouse_scroll)
        
        self.update_plot()
    
    def update_plot(self):
        self.plot.update_plot()
        self.canvas.draw()
        
        self.root.after(10, self.update_plot)

root = tk.Tk()
app = MainWindow(root)
root.mainloop()

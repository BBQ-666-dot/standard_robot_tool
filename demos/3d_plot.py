import tkinter as tk
from mpl_toolkits.mplot3d import Axes3D
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
        
        self.ax.view_init(elev=30, azim=30)
        self.ax.dist = 10
    
    def update_plot(self):
        x = np.random.rand(10)
        y = np.random.rand(10)
        z = np.random.rand(10)
        
        self.ax.cla()
        self.ax.scatter(x, y, z)
    
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
            self.ax.view_init(elev=self.ax.elev - dy, azim=self.ax.azim + dx)
        elif self.ax._dragging:
            dx = event.x - self.ax._drag_start[0]
            dy = event.y - self.ax._drag_start[1]
            self.ax._drag_start = (event.x, event.y)
            self.ax.azim -= dx * 0.3
        
        plt.draw()

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("实时三维绘图")
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        self.plot = RealTimePlot(self.ax)
        
        self.canvas.mpl_connect('button_press_event', self.plot.on_button_press)
        self.canvas.mpl_connect('button_release_event', self.plot.on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self.plot.on_mouse_move)
        
        self.update_plot()
    
    def update_plot(self):
        self.plot.update_plot()
        self.canvas.draw()
        
        self.root.after(100, self.update_plot)

root = tk.Tk()
app = MainWindow(root)
root.mainloop()

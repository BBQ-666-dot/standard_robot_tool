import tkinter as tk

class Page_Robot_State(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.id = 3
    
    def CreatePage(self):
        pass
        tk.Label(self, text='机器人数据页面').pack(pady=(50, 0))
    
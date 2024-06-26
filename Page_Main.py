import tkinter as tk

class Page_Main(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.id = 1
    
    def CreatePage(self):
        pass
        tk.Label(self, text='主页面').pack(pady=(50, 0))
    
import tkinter as tk

class Page_Debug(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.id = 2
    
    def CreatePage(self):
        pass
        tk.Label(self, text='调试页面').pack(pady=(50, 0))
    
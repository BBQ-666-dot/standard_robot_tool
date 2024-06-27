import tkinter as tk
from CustomWidget import DataNameModel,PlotGraphModel

class Page_Debug(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.id = 2
    
    def CreatePage(self,width:int,height:int):
        pass
        tk.Label(self, text='调试页面').pack(pady=(50, 0))
        
        # 左边为数据名称列表，右边为绘图区域
        left_width = width*0.3
        right_width = width - left_width
        height = height - 20
        # 数据名称列表模块
        self.data_name_moodel = DataNameModel(self)
        self.data_name_moodel.place(x=0, y=10, width=left_width, height=height)
        
        # 图像绘制模块
        self.plot_graph_model = PlotGraphModel(self)
        self.plot_graph_model.place(x=left_width, y=10, width=right_width, height=height)
    
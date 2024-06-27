import tkinter as tk
from CustomWidget import DataNameModel,PlotGraphModel
from lib.data_procecss import Data_Process

class Page_Debug(tk.Frame):
    def __init__(self, master,data_process:Data_Process, **kwargs):
        super().__init__(master, **kwargs)
        self.id = 2
        self.data_process = data_process
    
    def CreatePage(self,width:int,height:int):
        # 左边为数据名称列表，右边为绘图区域
        left_width = width*0.3
        right_width = width - left_width
        height = height - 20
        
        # 开始绘图按钮
        self.label_toggle_plot = tk.Label(self, bg='red')
        self.label_toggle_plot.place(x=10, y=10, width=30, height=30)
        
        self.button_toggle_Port = tk.Button(
                        self,
                        text='开始绘图',
                        font=('黑体', 12),
                        width=10,height=1,
                        command=self.TogglePlot
                    )
        self.button_toggle_Port.place(x=40, y=10, width=100, height=30)

        # 数据名称列表模块
        self.data_name_moodel = DataNameModel(self)
        self.data_name_moodel.place(x=0, y=50, width=left_width, height=height-40)
        
        # 图像绘制模块
        self.plot_graph_model = PlotGraphModel(self)
        self.plot_graph_model.place(x=left_width, y=10, width=right_width, height=height)
    
    def TogglePlot(self):
        return
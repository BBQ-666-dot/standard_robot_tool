import tkinter as tk
import tkinter.ttk
import tkinter.messagebox
import sys
import os
from PIL import Image, ImageTk
import base64
from io import BytesIO
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

import picture

PaymentQRCode_ROI=(100, 50, 650, 700)
PaymentQRCodeImage = Image.open(BytesIO(base64.b64decode(picture.PaymentQRCode_base64))).crop(PaymentQRCode_ROI)

def App_path():
    """获得主程序的路径"""
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)  #使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__)            #没打包前的py目录


def RunAbout():
    asp = About_Serial_Print()
    asp.InitUI()
    asp.RunApp()


def RunHowToUse():
    htu = How_To_Use()
    htu.InitUI()
    htu.RunApp()


def RunPay():
    pay = Pay()
    pay.InitUI()
    pay.RunApp()
    

class About_Serial_Print():
    def __init__(self) -> None:
        pass
    
    
    def InitUI(self):
        self.root = tk.Tk()
        self.root.title('About Serial Output APP')
        self.root.geometry('200x150')
        self.root.resizable(0,0)
        self.InitFrame()
        
        
    def InitFrame(self):
        About_Author = '作者：小企鹅\n创作于2023-6-6'
        Label_About_Author = tk.Label(
            self.root, 
            text=About_Author, 
            font=('黑体', 12), 
            width=30, height=2
            # anchor='w'
            )
        Label_About_Author.pack(side=tk.TOP,pady=10)
        
        Version = '当前版本：V1.5.0\n更新于：2023-7-25'
        Label_Version = tk.Label(
            self.root, 
            text=Version, 
            font=('黑体', 12), 
            width=30, height=2
            # anchor='w'
            )
        Label_Version.pack(side=tk.TOP,pady=10)
        
        
    def RunApp(self):
        self.root.mainloop()
        

class How_To_Use():
    def __init__(self) -> None:
        pass
    
    
    def InitUI(self):
        self.root = tk.Tk()
        self.root.title('如何使用本程序')
        self.root.geometry('510x300')
        self.root.resizable(0,0)
        self.InitFrame()
        self.AddHelp()
        
        
    def InitFrame(self):
        Frame_Text_How_To_Use = tk.Frame(self.root)
        Frame_Text_How_To_Use.pack(side=tk.TOP,pady=10)
        
        self.Text_How_To_Use = tk.Text(
            Frame_Text_How_To_Use,
            width=60,height=20,
            font=('黑体', 12)
        )
        self.Text_How_To_Use.pack(side=tk.LEFT)
        
        Text_How_To_Use_Scroll = tk.Scrollbar(Frame_Text_How_To_Use)
        Text_How_To_Use_Scroll.pack(side=tk.RIGHT,fill=tk.Y)
        # 关联滚动条和文本框
        Text_How_To_Use_Scroll.config(command=self.Text_How_To_Use.yview)
        self.Text_How_To_Use.config(yscrollcommand=Text_How_To_Use_Scroll.set)
        
        
    def AddHelp(self):
        self.Text_How_To_Use.insert(tk.END, ' '*26+'使用帮助\n')
        self.Text_How_To_Use.insert(tk.END, '0 如何打赏\n')
        self.Text_How_To_Use.insert(tk.END, '  点击菜单栏的打赏按钮，扫码打赏小钱钱\n')
        self.Text_How_To_Use.insert(tk.END, '\n')
        self.Text_How_To_Use.insert(tk.END, '------------------------------------------------------------\n')
        self.Text_How_To_Use.insert(tk.END, '\n')
        self.Text_How_To_Use.insert(tk.END, '1 开始使用\n')
        self.Text_How_To_Use.insert(tk.END, '1.1 串口参数的选择\n')
        self.Text_How_To_Use.insert(tk.END, '1.1.1 端口号\n')
        self.Text_How_To_Use.insert(tk.END, '      如果显示无端口则表示没有识别到端口，重新插拔一下\n')
        self.Text_How_To_Use.insert(tk.END, '      下拉列表中为当前可用的端口，选择需要使用的端口即可\n')
        self.Text_How_To_Use.insert(tk.END, '1.1.2 波特率\n')
        self.Text_How_To_Use.insert(tk.END, '      一般使用默认值即可\n')
        self.Text_How_To_Use.insert(tk.END, '1.1.3 采样点个数\n')
        self.Text_How_To_Use.insert(tk.END, '      存储的数据个数，可以自由调节\n')
        self.Text_How_To_Use.insert(tk.END, '      1.可以直接修改输入框内的数量\n')
        self.Text_How_To_Use.insert(tk.END, '      2.直接通过鼠标滚轮上下滚动来增减数值\n')
        self.Text_How_To_Use.insert(tk.END, '\n')
        self.Text_How_To_Use.insert(tk.END, '1.2 串口的开关\n')
        self.Text_How_To_Use.insert(tk.END, '    点击开启串口按钮，如果指示方块变成绿色则代表串口开启成功\n')
        self.Text_How_To_Use.insert(tk.END, '    再次点击按钮，如果指示方块变成绿色则代表串口关闭成功\n')
        self.Text_How_To_Use.insert(tk.END, '\n')
        self.Text_How_To_Use.insert(tk.END, '1.3 输出数据\n')
        self.Text_How_To_Use.insert(tk.END, '1.3.1 设置输出内容\n')
        self.Text_How_To_Use.insert(tk.END, '      选择输出的内容是解码后的数据还是原始的二进制数据\n')
        self.Text_How_To_Use.insert(tk.END, '      选择是否输出时间戳信息\n')
        self.Text_How_To_Use.insert(tk.END, '\n')
        self.Text_How_To_Use.insert(tk.END, '1.4 绘制图像\n')
        self.Text_How_To_Use.insert(tk.END, '1.4.1 选择输出图像的数据标签\n')
        self.Text_How_To_Use.insert(tk.END, '      数据标签下拉列表中为接收到的数据标签，选择想要绘制的数据标签\n')
        self.Text_How_To_Use.insert(tk.END, '\n')
        self.Text_How_To_Use.insert(tk.END, '------------------------------------------------------------\n')
        self.Text_How_To_Use.insert(tk.END, '\n')
        self.Text_How_To_Use.insert(tk.END, '2 C板代码配置\n')
        self.Text_How_To_Use.insert(tk.END, '2.1 type编码\n')
        self.Text_How_To_Use.insert(tk.END, '    0 - int\n')
        self.Text_How_To_Use.insert(tk.END, '    1 - float\n')
        self.Text_How_To_Use.insert(tk.END, '\n')
        self.Text_How_To_Use.insert(tk.END, '------------------------------------------------------------\n')
        self.Text_How_To_Use.insert(tk.END, '\n')
        self.Text_How_To_Use.insert(tk.END, '3 常见错误\n')

        self.Text_How_To_Use.configure(state='disabled')
        
        
    def RunApp(self):
        self.root.mainloop()
        
        
class Pay():
    def __init__(self) -> None:
        pass
    
    
    def InitUI(self):
        self.root = tk.Tk()
        self.root.title('给小企鹅打赏一点小钱钱呗[感动]')
        self.root.geometry('550x650')
        self.root.resizable(0,0)
        # self.PaymentQRCode = ImageTk.PhotoImage(PaymentQRCodeImage)
        self.fig = plt.figure()
        self.fig.subplots_adjust(left=0, right=1, bottom=0.01, top=1)  # 设置页边距
        plt.imshow(PaymentQRCodeImage)
        plt.axis('off')  # 可选：关闭坐标轴
        self.InitFrame()
        
        
    def InitFrame(self):
        Label_Pay = tk.Label(
            self.root,
            text='如果觉得好用\n就给小企鹅打赏一点小钱钱呗[感动]',
            font=('黑体', 25),
            bg='white',
        )
        Label_Pay.pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        
        self.canvas = FigureCanvasTkAgg(
                        figure=self.fig, 
                        master=self.root
                    )
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        
    def RunApp(self):
        self.root.mainloop()
        
if __name__ == '__main__':
    # RunAbout()
    RunHowToUse()
    # RunPay()
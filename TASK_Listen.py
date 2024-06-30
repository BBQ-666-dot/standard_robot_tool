import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from OperationTypedef import OPEN_USB,STOP_APP,ERROR

from pynput import mouse, keyboard
import time
import threading

STOP = False


class Input_Listener():
    def __init__(self, input_listener:dict,oprations:list, run_time:dict):
        self.input_listener = input_listener
        self.oprations = oprations
        self.run_time = run_time
        # 监听键盘
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        
        # 监听鼠标
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_move=self.on_move,
            on_scroll=self.on_scroll)
    
    def start(self):
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
        self.keyboard_listener.join()
        self.mouse_listener.join()
        return
    
    def stop(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        return

    ############################################################
    #  监听任务
    #  on_press 
    #  on_release
    #  on_click
    #  on_move
    #  on_scroll
    ############################################################
    def on_press(self,key):
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False

        try:
            print(f'按键 {key.char} 被按下')
        except AttributeError:
            print(f'特殊按键 {key} 被按下')
        # if key == keyboard.Key.esc:
        #     # 按下Esc键停止监听
        #     return False

    def on_release(self,key):
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False
        
        print(f'按键 {key} 被释放')
        # if key == keyboard.Key.esc:
        #     # 按下Esc键停止监听
        #     return False

    def on_click(self,x, y, button, pressed):
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False
        
        if pressed:
            print(f'鼠标点击了 {button} 在位置 ({x}, {y})')
        else:
            print(f'鼠标释放了 {button} 在位置 ({x}, {y})')

    def on_move(self,x, y):
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False
        
        print(f'鼠标移动到 ({x}, {y})')

    def on_scroll(self,x, y, dx, dy):
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False
        
        print(f'鼠标在 ({x}, {y}) 滚动了 {dx}, {dy}')


def TASK_Listen(input_listener:dict,oprations:list, run_time:dict):
    LogInfo("开始运行 StandardRobot++ 上位机的输入模块")
    
    input_listener = Input_Listener(input_listener,oprations, run_time)
    input_listener.start()

    LogInfo("结束运行 StandardRobot++ 上位机的输入模块")
    
if __name__ == "__main__":
    input_listener = {}
    oprations = []
    run_time = {}

    listen_task_thread = threading.Thread(target=TASK_Listen, args=(input_listener,oprations,run_time))
    listen_task_thread.start()
    
    time.sleep(2)
    oprations.append(STOP_APP)
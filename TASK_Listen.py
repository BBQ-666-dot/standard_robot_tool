import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from OperationTypedef import OPEN_USB,STOP_APP,ERROR

from pynput import mouse, keyboard
import time
import threading

STOP = False

MAX_VX = 3
MAX_VY = 3
MAX_WZ = 3

MAX_CHASSIS_ROLL = 0.3


class Input_Listener():
    def __init__(self, input_listener:dict,oprations:list, run_time:dict,robot_cmd:dict):
        self.input_listener = input_listener
        self.oprations = oprations
        self.run_time = run_time
        self.robot_cmd = robot_cmd
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
            if key.char == "w":
                self.robot_cmd['speed_vector']['vx'] = MAX_VX
            elif key.char == "s":
                self.robot_cmd['speed_vector']['vx'] = -MAX_VX
            elif key.char == "a":
                self.robot_cmd['speed_vector']['vy'] = MAX_VY
            elif key.char == "d":
                self.robot_cmd['speed_vector']['vy'] = -MAX_VY
            elif key.char == "q":
                if self.robot_cmd['chassis']['roll'] < MAX_CHASSIS_ROLL-0.01:
                    self.robot_cmd['chassis']['roll'] = MAX_CHASSIS_ROLL
                else:
                    self.robot_cmd['chassis']['roll'] = 0
            elif key.char == "e":
                if self.robot_cmd['chassis']['roll'] > -MAX_CHASSIS_ROLL+0.01:
                    self.robot_cmd['chassis']['roll'] = -MAX_CHASSIS_ROLL
                else:
                    self.robot_cmd['chassis']['roll'] = 0
                
            print(f'vx={self.robot_cmd["speed_vector"]["vx"]}')
            print(f'vy={self.robot_cmd["speed_vector"]["vy"]}')
            print(f'wz={self.robot_cmd["speed_vector"]["wz"]}')
            print(f'按键 {key} 被按下')
        except AttributeError:
            print(f'特殊按键 {key} 被按下')

    def on_release(self,key):
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False
        
        try:
            if key.char == "w" or key.char == "s":
                self.robot_cmd['speed_vector']['vx'] = 0
            elif key.char == "a" or key.char == "d":
                self.robot_cmd['speed_vector']['vy'] = 0
            print(f'vx={self.robot_cmd["speed_vector"]["vx"]}')
            print(f'vy={self.robot_cmd["speed_vector"]["vy"]}')
            print(f'wz={self.robot_cmd["speed_vector"]["wz"]}')
        except AttributeError:
            print(f'特殊按键 {key} 被按下')

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

def FeedDog(input_listener:Input_Listener,oprations:list,run_time:dict):
    while True:
        if len(oprations)>0 and (oprations[0] == STOP_APP or (ERROR in oprations)):
            input_listener.stop()
            break
        run_time['TASK_Listen'] = int(time.time() * 1000)
        time.sleep(0.02)

def TASK_Listen(oprations:list, run_time:dict, robot_cmd:dict):
    LogInfo("开始运行 StandardRobot++ 上位机的输入模块")
    
    input_listener = Input_Listener(input,oprations, run_time, robot_cmd)
    feed_dog_thread = threading.Thread(target=FeedDog, args=(input_listener,oprations,run_time))
    
    feed_dog_thread.start()
    input_listener.start()

    LogInfo("结束运行 StandardRobot++ 上位机的输入模块")
    
if __name__ == "__main__":
    oprations = []
    run_time = {}
    robot_cmd = {
        'speed_vector':{
            'vx':0,
            'vy':0,
            'wz':0
        },
        'chassis':{
            'roll':0
        },
        'gimbal':{
            'pitch':0,
            'yaw':0
        }
    }

    listen_task_thread = threading.Thread(target=TASK_Listen, args=(oprations,run_time,robot_cmd))
    listen_task_thread.start()
    
    time.sleep(1)
    oprations.append(STOP_APP)
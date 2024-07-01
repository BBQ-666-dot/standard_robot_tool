import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from OperationTypedef import OPEN_USB,STOP_APP,ERROR

from pynput import mouse, keyboard
import time
import threading
import math

import pygame
from pygame.locals import *

STOP = False

MAX_VX = 3
MAX_VY = 3
MAX_WZ = 3

MAX_CHASSIS_ROLL = 0.3

keboard_cmd = {
                'time_stamp': 0,
                'speed_vector': {
                        'vx': 0,
                        'vy': 0,
                        'wz': 0,
                        },
                'chassis': {
                        'roll': 0,
                        'yaw': 0,
                        'pitch': 0,
                        'leg_length': 0,
                        },
                'gimbal': {
                        'yaw': 0,
                        'pitch': 0,
                        },
                'shoot': {
                        'fire': 0,
                        'fric_on': 0,
                        },
            }

joystick_cmd = {
                'time_stamp': 0,
                'speed_vector': {
                        'vx': 0,
                        'vy': 0,
                        'wz': 0,
                        },
                'chassis': {
                        'roll': 0,
                        'yaw': 0,
                        'pitch': 0,
                        'leg_length': 0,
                        },
                'gimbal': {
                        'yaw': 0,
                        'pitch': 0,
                        },
                'shoot': {
                        'fire': 0,
                        'fric_on': 0,
                        },
            }

use_cmd = 'keboard'

class Input_Listener():
    def __init__(self, input_listener:dict,oprations:list, run_time:dict,robot_cmd:dict):
        self.input_listener = input_listener
        self.oprations = oprations
        self.run_time = run_time
        self.robot_cmd = robot_cmd
        
        self.last_x = None
        self.last_y = None
        
        # 监听键盘
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        
        # 监听鼠标
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_move=self.on_move,
            on_scroll=self.on_scroll)
        return
    
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
        global use_cmd
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False
        if use_cmd == 'keboard':
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
        global use_cmd
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False
        
        if use_cmd == 'keboard':
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
        global use_cmd
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False
        
        if self.last_x is None or self.last_y is None:
            self.last_x = x
            self.last_y = y
            return

        # Calculate the distance moved
        dx = x - self.last_x
        dy = y - self.last_y
        
        # Update the last position
        self.last_x = x
        self.last_y = y
        
        if use_cmd == 'keboard':
            self.robot_cmd["gimbal"]["yaw"] += dx * 0.01
            if self.robot_cmd["gimbal"]["yaw"] > math.pi:
                self.robot_cmd["gimbal"]["yaw"] -= 2*math.pi
            elif self.robot_cmd["gimbal"]["yaw"] < -math.pi:
                self.robot_cmd["gimbal"]["yaw"] += 2*math.pi
            
            self.robot_cmd["gimbal"]["pitch"] += dy * 0.01
            if self.robot_cmd["gimbal"]["pitch"] > math.pi/2:
                self.robot_cmd["gimbal"]["pitch"] = math.pi/2
            elif self.robot_cmd["gimbal"]["pitch"] < -math.pi/2:
                self.robot_cmd["gimbal"]["pitch"] = -math.pi/2

    def on_scroll(self,x, y, dx, dy):
        if STOP_APP in self.oprations or ERROR in self.oprations:
            self.stop()
            return False
        
        print(f'鼠标在 ({x}, {y}) 滚动了 {dx}, {dy}')

class Joystick_Listener():
    def __init__(self,robot_cmd:dict) -> None:
        self.robot_cmd = robot_cmd
        
        self.listen = False
        self.joystick = None
        return
    
    def init_pygame(self):
        # 初始化pygame
        pygame.init()
        pygame.joystick.init()  # 初始化手柄支持
        return

    def detect_joystick(self):
        global use_cmd
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            if self.joystick == None:
                self.joystick = pygame.joystick.Joystick(0)
            # print(f"init：{self.joystick.get_init()}")
            if self.joystick.get_init() == False:
                self.joystick.init()
            use_cmd = 'joystick'
        else:
            LogWarning("未检测到手柄！")
            self.joystick = None
            use_cmd = 'keboard'

    # 更新手柄数据的函数
    def update_joystick_data(self):
        global use_cmd
        if self.joystick == None:
            return
        pygame.event.pump()  # 更新pygame事件队列

        # 更新轴数据
        axis_data = [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())]
        axis_text = "轴数据：" + ", ".join([f"{x:.2f}" for x in axis_data])

        # 更新按钮数据
        button_data = [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]
        button_text = "按钮状态：" + ", ".join([str(x) for x in button_data])
        
        if use_cmd == 'joystick':
            self.robot_cmd['speed_vector']['vx'] = self.joystick.get_axis(0) * MAX_VX
            self.robot_cmd['speed_vector']['vy'] = self.joystick.get_axis(1) * MAX_VY
            
            self.robot_cmd['gimbal']['yaw'] += self.joystick.get_axis(2) * 0.01
            if self.robot_cmd['gimbal']['yaw'] > math.pi:
                self.robot_cmd['gimbal']['yaw'] -= 2*math.pi
            elif self.robot_cmd['gimbal']['yaw'] < -math.pi:
                self.robot_cmd['gimbal']['yaw'] += 2*math.pi
            
            self.robot_cmd['gimbal']['pitch'] += self.joystick.get_axis(3) * 0.01
            if self.robot_cmd['gimbal']['pitch'] > math.pi/2:
                self.robot_cmd['gimbal']['pitch'] = math.pi/2
            elif self.robot_cmd['gimbal']['pitch'] < -math.pi/2:
                self.robot_cmd['gimbal']['pitch'] = -math.pi/2
        return


def FeedDog(input_listener:Input_Listener,oprations:list,run_time:dict):
    while True:
        if len(oprations)>0 and (oprations[0] == STOP_APP or (ERROR in oprations)):
            input_listener.stop()
            break
        run_time['TASK_Listen'] = int(time.time() * 1000)
        time.sleep(0.02)
    return

def ListenJoystick(joystick_listener:Joystick_Listener,oprations:list):
    joystick_listener.init_pygame()
    while True:
        if len(oprations)>0 and (oprations[0] == STOP_APP or (ERROR in oprations)):
            break
        joystick_listener.detect_joystick()
        joystick_listener.update_joystick_data()
        time.sleep(0.01)
    return

def TASK_Listen(oprations:list, run_time:dict, robot_cmd:dict):
    global joystick_cmd , keboard_cmd
    LogInfo("开始运行 StandardRobot++ 上位机的输入模块")
    
    joystick_listener = Joystick_Listener(robot_cmd)
    input_listener = Input_Listener(input,oprations, run_time, robot_cmd)
    
    joystick_listen_thread = threading.Thread(target=ListenJoystick, args=(joystick_listener,oprations))
    feed_dog_thread = threading.Thread(target=FeedDog, args=(input_listener,oprations,run_time))
    
    feed_dog_thread.start()
    time.sleep(0.5) #等待其他线程启动
    joystick_listen_thread.start()
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
    
    time.sleep(10)
    oprations.append(STOP_APP)
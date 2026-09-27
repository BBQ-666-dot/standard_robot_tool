'''
StandardRobot++ 上位机主程序
'''
import AddLib
AddLib.add_lib()

from lib.log_info import LogError , LogInfo , LogWarning
from lib.usb_divice import USB_Device
from lib.data_procecss import Data_Process

from Window import Window
from OperationTypedef import OPEN_USB,STOP_APP
from TASK_UsbDevice import TASK_UsbDevice
from TASK_Monitor import TASK_Monitor
from TASK_Test import TASK_Test
from TASK_Listen import TASK_Listen
from TASK_UsbSend import TASK_UsbSend

import threading
import sys

LogInfo("开始运行 StandardRobot++ 上位机")

usb = USB_Device()
data_process = Data_Process()
operation_list = []
run_time = {}
robot_cmd = {
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


usb_divice_task_thread = threading.Thread(
                            target=TASK_UsbDevice, 
                            args=(usb, data_process, operation_list, run_time)
                        )
usb_divice_task_thread.start()

usb_send_task_thread = threading.Thread(
                            target=TASK_UsbSend, 
                            args=(usb,data_process,operation_list,run_time,robot_cmd)
                        )
usb_send_task_thread.start()

monitor_task_thread = threading.Thread(
                            target=TASK_Monitor, 
                            args=(usb, data_process, operation_list, run_time)
                        )
monitor_task_thread.start()

listen_task_thread = threading.Thread(
                            target=TASK_Listen, 
                            args=(operation_list, run_time, robot_cmd)
                        )
listen_task_thread.start()

if False:
    test_task_thread = threading.Thread(target=TASK_Test, args=(usb, data_process, operation_list, run_time))
    test_task_thread.start()

window = Window(usb, data_process, operation_list, run_time, robot_cmd)

window.InitApp(width=1240, height=700)

# 可选: --page main/debug/cmd/log 直接打开指定页面(方便调试与截图)
# 可选: --demo 启动时自动开启演示数据
if '--page' in sys.argv:
    try:
        page = sys.argv[sys.argv.index('--page') + 1].lower()
    except IndexError:
        page = 'main'
    if page == 'debug':
        window.SwitchPage(window.page_debug.id)
    elif page in ('cmd', 'robotcmd', 'robot'):
        window.SwitchPage(window.page_robot_cmd.id)
    elif page in ('monitor', 'mon'):
        window.SwitchPage(window.page_monitor.id)
    elif page == 'log':
        window.SwitchPage(window.page_log.id)
    else:
        window.SwitchPage(window.page_main.id)

if '--demo' in sys.argv:
    window.ToggleDemo()

if '--autoplot' in sys.argv:
    window.page_debug.TogglePlot()

# 可选: --port COMx 启动后自动打开指定串口(调试用)
if '--port' in sys.argv:
    try:
        port = sys.argv[sys.argv.index('--port') + 1]
    except IndexError:
        port = None
    if port:
        window.usb.modify(port, 9600, 8, 1, "N")
        window.operations.append(OPEN_USB)

window.RunApp()


LogInfo("结束运行 StandardRobot++ 上位机")

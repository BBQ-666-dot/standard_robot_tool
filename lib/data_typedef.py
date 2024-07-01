
# class Data():
#     def __init__(self) -> None:
#         self.latest = {}
#         self.

# DATA_ID_DEBUG = 1
# DATA_ID_IMU = 2
# DATA_ID_ROBOT_INFO = 3

SEND_ID_ROBOT_CMD = 1

class Imu_Data():
    def __init__(self) -> None:
        self.latest = {
            "time_stamp":0, # 时间戳(s)
            
            "yaw":0,   # 偏航角(rad)
            "pitch":0, # 俯仰角(rad)
            "roll":0,  # 横滚角(rad)
            
            "yaw_vel":0,   # 偏航角速度(rad/s)
            "pitch_vel":0, # 俯仰角速度(rad/s)
            "roll_vel":0,  # 横滚角速度(rad/s)
        }
        
        self.storage = {
            "time_stamp":[],
            
            "yaw":[],
            "pitch":[],
            "roll":[],
            
            "yaw_vel":[],
            "pitch_vel":[],
            "roll_vel":[],
        }
        self.length = len(self.storage['time_stamp'])
        return

    ############################################################
    #  基本功能
    #  update 更新数据
    #  clear 清空数据
    #  limit 限制数据长度
    ############################################################

    def update(self,data:dict) -> None:
        self.latest = data.copy()
        
        self.storage['time_stamp'].append(data['time_stamp'])
        
        self.storage['yaw'].append(data['yaw'])
        self.storage['pitch'].append(data['pitch'])
        self.storage['roll'].append(data['roll'])
        
        self.storage['yaw_vel'].append(data['yaw_vel'])
        self.storage['pitch_vel'].append(data['pitch_vel'])
        self.storage['roll_vel'].append(data['roll_vel'])
        
        self.length = len(self.storage['time_stamp'])
        return
    
    def clear(self) -> None:
        self.latest = {
            "yaw":0,
            "pitch":0,
            "roll":0,
            
            "yaw_vel":0,
            "pitch_vel":0,
            "roll_vel":0,
        }
        
        for key in self.storage:
            self.storage[key].clear()
        
        self.length = len(self.storage['time_stamp'])
        return
    
    def limit(self,length:int) -> None:
        for key in self.storage:
            self.storage[key] = self.storage[key][-length:]
        self.length = len(self.storage['time_stamp'])
        return
        
        
class Debug_Data():
    def __init__(self) -> None:
        self.latest = {
            "time_stamp":0, # 时间戳(s)
            "datas":{}, # 数据
        }
        
        self.storage = {
            "time_stamp":[],
            "datas":{},
        }
        self.length = len(self.storage['time_stamp'])
        return
    
    ############################################################
    #  基本功能
    #  update 更新数据
    #  clear 清空数据
    #  limit 限制数据长度
    ############################################################

    def update(self,data:dict) -> None:
        self.latest = data.copy()
        
        self.storage['time_stamp'].append(data['time_stamp'])
        
        for key in data['datas']:
            if key not in self.storage['datas']:
                self.storage['datas'][key] = []
            self.storage['datas'][key].append(data['datas'][key])
        
        self.length = len(self.storage['time_stamp'])
        return

    def clear(self) -> None:
        self.latest = {
            "time_stamp":0, # 时间戳(s)
            
            "datas":{}, # 数据
        }
        
        self.storage["time_stamp"].clear()

        self.storage["datas"] = {}

        self.length = len(self.storage['time_stamp'])
        return

    def limit(self,length:int) -> None:
        self.storage['time_stamp'] = self.storage['time_stamp'][-length:]
        
        for key in self.storage['datas']:
            self.storage['datas'][key] = self.storage['datas'][key][-length:]
        
        self.length = len(self.storage['time_stamp'])
        return

class Robot_Info_Data():
    def __init__(self) -> None:
        self.clear()
        return
    ############################################################
    #  基本功能
    #  update 更新数据
    #  clear 清空数据
    ############################################################

    def update(self,data:dict) -> None:
        self.latest = data.copy()
        return

    def clear(self) -> None:
        self.latest = {
                'time_stamp': 0,
                'types': {
                        'chassis': 0,
                        'gimbal': 0,
                        'shoot': 0,
                        'arm': 0,
                        'custom_controller': 0,
                        },
                'state': {
                        'chassis':False,
                        'gimbal':False,
                        'shoot':False,
                        'arm':False,
                        'custom_controller':False,
                        },
                'speed_vector': {
                        'vx': 0,
                        'vy': 0,
                        'wz': 0,
                        },
            }
        return

class Robot_Cmd_Data():
    def __init__(self) -> None:
        self.clear()
        return
    ############################################################
    #  基本功能
    #  update 更新数据
    #  clear 清空数据
    ############################################################

    def update(self,data:dict) -> None:
        self.latest = data.copy()
        return

    def clear(self) -> None:
        self.latest = {
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
        return
    





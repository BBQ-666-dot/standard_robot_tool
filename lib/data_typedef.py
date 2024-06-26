
# class Data():
#     def __init__(self) -> None:
#         self.latest = {}
#         self.

class Imu_Data():
    def __init__(self) -> None:
        self.latest = {
            "yaw":0,
            "pitch":0,
            "roll":0,
            
            "yaw_vel":0,
            "pitch_vel":0,
            "roll_vel":0,
        }
        
        self.storage = {
            "yaw":[],
            "pitch":[],
            "roll":[],
            
            "yaw_vel":[],
            "pitch_vel":[],
            "roll_vel":[],
        }

############################################################
#  基本功能
#  update 更新数据
#  clear 清空数据
############################################################

    def update(self,data:dict):
        self.latest = data.copy()
        
        self.storage['yaw'].append(data['yaw'])
        self.storage['pitch'].append(data['pitch'])
        self.storage['roll'].append(data['roll'])
        
        self.storage['yaw_vel'].append(data['yaw_vel'])
        self.storage['pitch_vel'].append(data['pitch_vel'])
        self.storage['roll_vel'].append(data['roll_vel'])
    
    def clear(self):
        self.latest = {
            "yaw":0,
            "pitch":0,
            "roll":0,
            
            "yaw_vel":0,
            "pitch_vel":0,
            "roll_vel":0,
        }

        self.storage["yaw"].clear()
        self.storage["pitch"].clear()
        self.storage["roll"].clear()
        
        self.storage["yaw_vel"].clear()
        self.storage["pitch_vel"].clear()
        self.storage["roll_vel"].clear()
        
        


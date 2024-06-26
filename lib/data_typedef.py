
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
############################################################

    def update(self,data:dict):
        pass

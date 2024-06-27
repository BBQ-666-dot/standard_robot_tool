'''
用于处理接收和发送数据的类
'''

from log_info import LogError , LogInfo , LogWarning
import CRC8_CRC16 as crc
import struct
from data_typedef import Imu_Data,Debug_Data

TIME_STAMP_OFFEST = 4

# imu数据的偏移量
YAW_OFFEST = 8
PITCH_OFFEST = 12
ROLL_OFFEST = 16

YAW_VEL_OFFEST = 20
PITCH_VEL_OFFEST = 24
ROLL_VEL_OFFEST = 28

class Data_Process():
    def __init__(self) -> None:
        self.imu_data = Imu_Data()
        self.debug_data = Debug_Data()
        return 

############################################################
#  数据处理基本功能
#  receive 对接收到的数据进行处理并存储
#  send
#  clear 清空数据
############################################################

    def receive(self,received_data:bytes):
        # 解码帧头信息
        data_len = int(received_data[1])
        data_id = received_data[2]
        if data_id == 0: # 
            pass
        elif data_id == 1: # Debug数据
            data_dict = {}
            data_num = data_len//15 # 数据个数
            offset = 8
            for i in range(data_num):
                data_name = received_data[offset:offset+10].rstrip(b'\0').decode('utf-8')
                data_type = received_data[offset+10]
                raw_data  = received_data[offset+11:offset+15]
                if data_type == 0:
                    data = struct.unpack('<I', raw_data)[0]
                elif data_type == 1:
                    data = struct.unpack('<f', raw_data)[0]
                else:
                    data = 0
                    LogError("未知数据类型")
                # print(data_name,data_type,data)
                # print(data_name == '')
                offset += 15
                if data_name != '':
                    data_dict[data_name] = data

            debug = {
                "time_stamp":(struct.unpack('<I', received_data[TIME_STAMP_OFFEST : TIME_STAMP_OFFEST+4])[0])/1000,
                "datas":data_dict
            }
            self.debug_data.update(debug)
            # print(self.debug_data.latest)
            
        elif data_id == 2: # Imu数据
            imu = {
                "time_stamp":(struct.unpack('<I', received_data[TIME_STAMP_OFFEST : TIME_STAMP_OFFEST+4])[0])/1000,
                
                "yaw"  :struct.unpack('<f', received_data[YAW_OFFEST   : YAW_OFFEST + 4])[0],
                "pitch":struct.unpack('<f', received_data[PITCH_OFFEST : PITCH_OFFEST + 4])[0],
                "roll" :struct.unpack('<f', received_data[ROLL_OFFEST  : ROLL_OFFEST + 4])[0],
                
                "yaw_vel"  :struct.unpack('<f', received_data[YAW_VEL_OFFEST   : YAW_VEL_OFFEST + 4])[0],
                "pitch_vel":struct.unpack('<f', received_data[PITCH_VEL_OFFEST : PITCH_VEL_OFFEST + 4])[0],
                "roll_vel" :struct.unpack('<f', received_data[ROLL_VEL_OFFEST  : ROLL_VEL_OFFEST + 4])[0],
            }
            
            self.imu_data.update(imu)
            # print(self.imu_data.latest)
            
        elif data_id == 3:
            pass
        
        return 

    def send(self):
        pass
        return 
    
    def clear(self):
        self.imu_data.clear()
        return
'''
用于处理接收和发送数据的类
'''

from log_info import LogError , LogInfo , LogWarning
import struct
from data_typedef import Imu_Data,Debug_Data,Robot_Info_Data

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
        self.robot_info_data = Robot_Info_Data()
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
            
        elif data_id == 3: # 机器人信息数据
            TYPES_OFFSET = 8
            STATE_OFFSET = 10
            VX_OFFSET = 11
            VY_OFFSET = 15
            WZ_OFFSET = 19
            
            chassis_names = ['无底盘','麦轮底盘','全向轮底盘','舵轮底盘','平衡底盘']
            gimbal_names = ['无云台','yaw-pitch电机直连云台']
            shoot_names = ['无发射机构','摩擦轮+拨弹盘','气动+拨弹盘']
            arm_names = ['无机械臂','企鹅mini机械臂']
            custom_controller_names = ['无自定义控制器','企鹅mini自定义控制器']
            
            time_stamp = struct.unpack('<I', received_data[TIME_STAMP_OFFEST : TIME_STAMP_OFFEST+4])[0]
            print('time_stamp =',time_stamp)
            
            types_raw = struct.unpack('<H', received_data[TYPES_OFFSET : TYPES_OFFSET+2])[0]
            # chassis_id = types_raw>>13 & 0b111
            # gimbal_id = (types_raw>>10) & 0b111
            # shoot_id = (types_raw>>7) & 0b111
            # arm_id = (types_raw>>4) & 0b111
            # custom_controller_id = (types_raw>>1) & 0b111
            chassis_id =           types_raw & 0b0000000000001110
            gimbal_id =            types_raw & 0b0000000001110000
            shoot_id =             types_raw & 0b0000001110000000
            arm_id =               types_raw & 0b0001110000000000
            custom_controller_id = types_raw & 0b1110000000000000
            
            print('chassis id =',chassis_id)
            print('gimbal id =',gimbal_id)
            print('shoot id =',shoot_id)
            print('arm id =',arm_id)
            print('custom_controller id =',custom_controller_id)
            
            types = {
                'chassis': chassis_names[chassis_id],
                'gimbal': gimbal_names[gimbal_id],
                'shoot': shoot_names[shoot_id],
                'arm': arm_names[arm_id],
                'custom_controller': custom_controller_names[custom_controller_id],
            }
            
            state_raw = int(received_data[STATE_OFFSET])
            state = {
                'chassis':           bool(state_raw & 0b00001000),
                'gimbal':            bool(state_raw & 0b00010000),
                'shoot':             bool(state_raw & 0b00100000),
                'arm':               bool(state_raw & 0b01000000),
                'custom_controller': bool(state_raw & 0b10000000),
            }
            
            speed_vector = {
                'vx': struct.unpack('<f', received_data[VX_OFFSET:VX_OFFSET+4])[0],
                'vy': struct.unpack('<f', received_data[VY_OFFSET:VY_OFFSET+4])[0],
                'wz': struct.unpack('<f', received_data[WZ_OFFSET:WZ_OFFSET+4])[0],
            }
            
            robot_info = {
                'time_stamp': time_stamp,
                'types': types,
                'state': state,
                'speed_vector': speed_vector,
            }
            self.robot_info_data.update(robot_info)
        return 

    def send(self):
        pass
        return 
    
    def clear(self):
        self.imu_data.clear()
        return
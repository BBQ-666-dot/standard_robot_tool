'''
用于处理接收和发送数据的类
'''

from log_info import LogError , LogInfo , LogWarning
import struct
from data_typedef import Imu_Data,Debug_Data,Robot_Info_Data,Robot_Cmd_Data
from data_typedef import SEND_ID_ROBOT_CMD
import lib.CRC8_CRC16 as crc

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
        # receive data
        self.imu_data = Imu_Data()
        self.debug_data = Debug_Data()
        self.robot_info_data = Robot_Info_Data()
        
        # send data
        self.robot_cmd_data = Robot_Cmd_Data()
        
        self.sending_data = False
        return 

    def start_send(self):
        self.sending_data = True
        return
    
    def stop_send(self):
        self.sending_data = False
        return

############################################################
#  数据处理基本功能
#  receive 对接收到的数据进行处理并存储
#  send 发送数据
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
            
            types_raw = struct.unpack('<H', received_data[TYPES_OFFSET : TYPES_OFFSET+2])[0]
            types = {
                'chassis':           (types_raw>>0 ) & 0b111,
                'gimbal':            (types_raw>>3 ) & 0b111,
                'shoot':             (types_raw>>6 ) & 0b111,
                'arm':               (types_raw>>9 ) & 0b111,
                'custom_controller': (types_raw>>12) & 0b111,
            }
            
            state_raw = int(received_data[STATE_OFFSET])
            state = {
                'chassis':           bool((state_raw>>0 ) & 0b1),
                'gimbal':            bool((state_raw>>1 ) & 0b1),
                'shoot':             bool((state_raw>>2 ) & 0b1),
                'arm':               bool((state_raw>>3 ) & 0b1),
                'custom_controller': bool((state_raw>>4 ) & 0b1),
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
            # print(self.robot_info_data.latest)
        return 

    def send(self,send_id:int)->bytes:
        if not self.sending_data:
            return
        if send_id == SEND_ID_ROBOT_CMD:
            send_data = b'\x5a\x2a\x01' # sof + len + id
            send_data = crc.AppendCRC8(send_data)
            
            # 添加时间戳
            data = struct.pack('<I', self.robot_cmd_data.latest['time_stamp'])
            send_data += data
            # print(len(send_data))
            
            # 添加speed_vector数据
            data = struct.pack('<f', self.robot_cmd_data.latest['speed_vector']['vx'])
            send_data += data
            data = struct.pack('<f', self.robot_cmd_data.latest['speed_vector']['vy'])
            send_data += data
            data = struct.pack('<f', self.robot_cmd_data.latest['speed_vector']['wz'])
            send_data += data
            # print(len(send_data))
            
            # 添加chassis数据
            data = struct.pack('<f', self.robot_cmd_data.latest['chassis']['roll'])
            send_data += data
            data = struct.pack('<f', self.robot_cmd_data.latest['chassis']['pitch'])
            send_data += data
            data = struct.pack('<f', self.robot_cmd_data.latest['chassis']['yaw'])
            send_data += data
            data = struct.pack('<f', self.robot_cmd_data.latest['chassis']['leg_length'])
            send_data += data
            # print(len(send_data))
            
            # 添加gimbal数据
            data = struct.pack('<f', self.robot_cmd_data.latest['gimbal']['pitch'])
            send_data += data
            data = struct.pack('<f', self.robot_cmd_data.latest['gimbal']['yaw'])
            send_data += data
            # print(len(send_data))
            
            #添加shoot数据
            data = struct.pack('B', self.robot_cmd_data.latest['shoot']['fire'])
            send_data += data
            data = struct.pack('B', self.robot_cmd_data.latest['shoot']['fric_on'])
            send_data += data
            # print(len(send_data))
            
            #添加crc16校验
            send_data = crc.AppendCRC16(send_data)
            # print(len(send_data))
            
        return send_data
    
    def clear(self):
        self.imu_data.clear()
        return
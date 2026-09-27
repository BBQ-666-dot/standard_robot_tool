'''
用于处理接收和发送数据的类
'''

from log_info import LogError , LogInfo , LogWarning
import struct
import time
import threading
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
        self.send_period = 0.005 # 发送周期(s)
        self.stats = {
            'rx_frames': 0,
            'rx_errors': 0,
            'tx_packets': 0,
            'demo': False,
            'replaying': False,
            'ids': {},   # data_id -> {'count','last','period'}
        }

        # 录制/回放
        self.recording = False
        self.recorded = []      # [(t, raw_bytes), ...]
        self.replaying = False
        self.replay_thread = None
        self.replay_speed = 1.0
        return

    def start_send(self):
        self.sending_data = True
        return
    
    def stop_send(self):
        self.sending_data = False
        return

    def inject_imu(self, time_stamp, yaw, pitch, roll, yaw_vel, pitch_vel, roll_vel):
        '''演示模式：注入一帧IMU数据'''
        self.imu_data.update({
            "time_stamp": time_stamp,
            "yaw": yaw,
            "pitch": pitch,
            "roll": roll,
            "yaw_vel": yaw_vel,
            "pitch_vel": pitch_vel,
            "roll_vel": roll_vel,
        })
        self._record_id_stat(0x02)
        self.stats['rx_frames'] += 1
        return

    def inject_debug(self, time_stamp, datas:dict):
        '''演示模式：注入一帧调试数据'''
        self.debug_data.update({
            "time_stamp": time_stamp,
            "datas": dict(datas),
        })
        self._record_id_stat(0x01)
        self.stats['rx_frames'] += 1

    def _record_id_stat(self, data_id:int):
        '''记录某个数据包id的接收统计(周期EMA/总数/最后时间)'''
        now = time.time()
        entry = self.stats['ids'].get(data_id)
        if entry is None:
            self.stats['ids'][data_id] = {'count': 1, 'last': now, 'period': 0.05}
        else:
            dt = now - entry['last']
            if 0 < dt < 1.0:
                entry['period'] = entry['period'] * 0.9 + dt * 0.1
            entry['count'] += 1
            entry['last'] = now
        return

############################################################
#  数据处理基本功能
#  receive 对接收到的数据进行处理并存储
#  send 发送数据
#  clear 清空数据
############################################################

    def receive(self,received_data:bytes, from_replay:bool=False):
        # 录制原始数据帧(回放产生的不再录)
        if self.recording and (not from_replay):
            self.recorded.append((time.time(), bytes(received_data)))

        # 解码帧头信息
        data_len = int(received_data[1])
        data_id = received_data[2]

        # 通信统计(每个数据包id)
        self._record_id_stat(data_id)
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

    ############################################################
    #  录制 / 回放
    #  start_record  开始录制接收到的原始帧
    #  stop_record   停止录制, 返回录制帧数
    #  save_record   保存录制到文件(.pbr)
    #  load_record   从文件载入录制
    #  start_replay  开始回放(按原始时间间隔)
    #  stop_replay   停止回放
    ############################################################
    def start_record(self):
        self.recorded = []
        self.recording = True
        LogInfo("开始录制数据(原始帧)")
        return

    def stop_record(self) -> int:
        self.recording = False
        count = len(self.recorded)
        LogInfo(f"停止录制, 共 {count} 帧")
        return count

    def save_record(self, path:str) -> bool:
        import pickle
        try:
            with open(path, 'wb') as f:
                pickle.dump(self.recorded, f, protocol=pickle.HIGHEST_PROTOCOL)
            LogInfo(f"录制已保存: {path} ({len(self.recorded)} 帧)")
            return True
        except Exception as e:
            LogError(f"保存录制失败: {e}")
            return False

    def load_record(self, path:str):
        import pickle
        try:
            with open(path, 'rb') as f:
                frames = pickle.load(f)
            LogInfo(f"录制已载入: {path} ({len(frames)} 帧)")
            return frames
        except Exception as e:
            LogError(f"载入录制失败: {e}")
            return []

    def start_replay(self, frames:list) -> bool:
        if self.replaying:
            LogWarning("回放进行中")
            return False
        if not frames:
            LogWarning("没有可回放的数据")
            return False
        self.replaying = True
        self.stats['replaying'] = True
        self.replay_thread = threading.Thread(target=self._replay_loop,
                                              args=(frames,), daemon=True)
        self.replay_thread.start()
        LogInfo(f"开始回放({len(frames)} 帧, {self.replay_speed:.1f}x)")
        return True

    def stop_replay(self):
        if self.replaying:
            self.replaying = False
            self.stats['replaying'] = False
            LogInfo("停止回放")
        return

    def _replay_loop(self, frames):
        t_begin = frames[0][0]
        wall_begin = time.time()
        for t, raw in frames:
            if not self.replaying:
                break
            target = wall_begin + (t - t_begin) / max(0.1, self.replay_speed)
            while self.replaying:
                wait = target - time.time()
                if wait <= 0:
                    break
                time.sleep(min(wait, 0.05))
            if not self.replaying:
                break
            try:
                self.receive(raw, from_replay=True)
                self.stats['rx_frames'] += 1
            except Exception:
                pass
        self.replaying = False
        self.stats['replaying'] = False
        LogInfo("回放结束")
        return
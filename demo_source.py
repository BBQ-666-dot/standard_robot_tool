'''
演示数据源
不接 C 板时模拟下位机发送的数据，便于预览界面与波形
IMU 数据按真实协议生成原始帧, 走正常解析路径(录制/抓包也能用)
'''
import math
import struct
import threading
import time

from lib.log_info import LogInfo
import lib.CRC8_CRC16 as crc


def make_imu_frame(ts_ms, yaw, pitch, roll, gx, gy, gz) -> bytes:
    '''按USB协议生成一帧IMU数据(id=0x02)'''
    body = struct.pack('<I', int(ts_ms))
    body += struct.pack('<f', yaw) + struct.pack('<f', pitch) + struct.pack('<f', roll)
    body += struct.pack('<f', gx) + struct.pack('<f', gy) + struct.pack('<f', gz)
    header = bytes([0x5A, len(body), 0x02])
    header = crc.AppendCRC8(header)
    frame = header + body
    return crc.AppendCRC16(frame)


class DemoSource:
    def __init__(self, data_process):
        self.data_process = data_process
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.data_process.stats['demo'] = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        LogInfo("演示模式已开启（模拟数据源）")

    def stop(self):
        if not self.running:
            return
        self.running = False
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=0.2) # 等待旧线程退出, 防止连点堆线程
        self.data_process.stats['demo'] = False
        LogInfo("演示模式已关闭")

    def toggle(self) -> bool:
        if self.running:
            self.stop()
        else:
            self.start()
        return self.running

    def _run(self):
        t0 = time.time()
        last_debug = 0.0
        while self.running:
            t = time.time() - t0

            yaw = math.sin(t * 0.9) * 1.8
            pitch = math.sin(t * 1.4) * 0.35
            roll = math.sin(t * 1.9 + 1.0) * 0.28
            yaw_vel = math.cos(t * 0.9) * 0.9 * 1.8
            pitch_vel = math.cos(t * 1.4) * 1.4 * 0.35
            roll_vel = math.cos(t * 1.9 + 1.0) * 1.9 * 0.28
            # IMU 走真实协议解析路径(原始帧 -> receive), 录制/抓包可用
            frame = make_imu_frame(t * 1000.0, yaw, pitch, roll,
                                   yaw_vel, pitch_vel, roll_vel)
            self.data_process.receive(frame)
            self.data_process.stats['rx_frames'] += 1

            if t - last_debug >= 0.02: # 50Hz 调试数据
                last_debug = t
                datas = {
                    "chassis_vx":  math.sin(t * 1.2) * 2.0,
                    "chassis_vy":  math.cos(t * 0.8) * 1.5,
                    "chassis_wz":  math.sin(t * 2.2) * 3.0,
                    "gimbal_yaw":  yaw,
                    "gimbal_pitch": pitch,
                    "shoot_speed": 18.0 + math.sin(t * 5.0) * 0.5,
                    # 模块通信状态(与下位机约定同名)
                    "motor1": 1.0, "motor2": 1.0, "motor3": 1.0, "motor4": 1.0,
                    "gimbal_y": 1.0, "gimbal_p": 1.0, "trigger": 1.0,
                    "referee": 1.0, "bmi088": 1.0, "remote_rc": 1.0,
                }
                # 周期性模拟 motor2 掉线, 演示异常检测与自动抓包
                if 20.0 <= (t % 40.0) <= 24.0:
                    datas["motor2"] = 0.0
                self.data_process.inject_debug(t, datas)
            time.sleep(0.005)

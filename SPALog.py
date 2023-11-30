from enum import Enum

# class Log_Level(Enum):
#     INFO = 0
#     WARNING = 1
#     ERROR = 2
#     DEBUG = 3

class Info_Index(Enum):
    Custom = -1 #自定义消息
    PortIsOpen = 0
    PortIsClose = 1
    PortIsReceivingData = 2
    PortIsNotReceivingData = 3

class Warning_Index(Enum):
    Custom = -1
    DoNotFindPort = 0
    HaveNotReceiveAnyData = 1
    
class Error_Index(Enum):
    Custom = -1
    PortTimeout = 0
    PortAbnormality = 1
    PortOpenFailed = 2
    PortReadFailed = 3
    
class Debug_Index(Enum):
    Custom = -1
    Debug = 0



def LogInfo(info_index:Info_Index, string="") -> None:
    if info_index == Info_Index.Custom:
        text = string
    elif info_index == Info_Index.PortIsOpen:
        text = "串口打开成功"
    elif info_index == Info_Index.PortIsClose:
        text = "串口关闭成功"
    elif info_index == Info_Index.PortIsReceivingData:
        text = "串口正在接收数据"
    elif info_index == Info_Index.PortIsNotReceivingData:
        text = "串口停止接收数据"
    else:
        text = string
    print(f"\033[92mINFO:{text}\033[0m")


def LogWarning(warning_index:Warning_Index , string="") -> None:
    if warning_index == Warning_Index.Custom:
        text = string
    elif warning_index == Warning_Index.DoNotFindPort:
        text = "未找到串口"
    elif warning_index == Warning_Index.HaveNotReceiveAnyData:
        text = "未接收到任何数据"
    else:
        text = string
    print(f"\033[93mWARNING:{text}\033[0m")


def LogError(error_index:Error_Index , string="") -> None:
    if error_index == Error_Index.Custom:
        text = string
    elif error_index == Error_Index.PortTimeout:
        text = "串口读取超时"
    elif error_index == Error_Index.PortAbnormality:
        text = "串口异常"
    elif error_index == Error_Index.PortOpenFailed:
        text = "串口打开失败"
    elif error_index == Error_Index.PortReadFailed:
        text = "串口读取失败"
    else:
        text = string
    print(f"\033[91mERROR:{text}\033[0m")

# def LogDebug(log_index:int , **kwargs):
    # text = Log()
    # print(f"\033[92m{text}\033[0m")
    


if __name__ == "__main__":
    LogInfo(Info_Index.PortIsOpen)
    LogInfo(Info_Index.PortIsClose)
    LogWarning(Warning_Index.DoNotFindPort)
    LogError(Error_Index.PortTimeout)
    LogError(Error_Index.PortIsAbnormallyClosed)
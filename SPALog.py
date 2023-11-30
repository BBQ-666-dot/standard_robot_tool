from enum import Enum

# class Log_Level(Enum):
#     INFO = 0
#     WARNING = 1
#     ERROR = 2
#     DEBUG = 3

class Info_Index(Enum):
    PortIsOpen = 0
    PortIsClose = 1
    PortIsReceivingData = 2
    PortIsNotReceivingData = 3

class Warning_Index(Enum):
    DoNotFindPort = 0
    
class Error_Index(Enum):
    PortTimeout = 0
    PortIsAbnormallyClosed = 1
    PortOpenFailed = 2
    
class Debug_Index(Enum):
    Debug = 0



def LogInfo(info_index:Info_Index, string="") -> None:
    if info_index == Info_Index.PortIsOpen:
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
    if warning_index == Warning_Index.DoNotFindPort:
        text = "未找到串口"
    else:
        text = string
    print(f"\033[93mWARNING:{text}\033[0m")


def LogError(error_index:Error_Index , string="") -> None:
    if error_index == Error_Index.PortTimeout:
        text = "串口读取超时"
    elif error_index == Error_Index.PortIsAbnormallyClosed:
        text = "串口异常关闭"
    elif error_index == Error_Index.PortOpenFailed:
        text = "串口打开失败"
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
import sys
import time
import queue
import threading


def LogInfo(string="") -> None:
    _emit("INFO", str(string))


def LogWarning(string="") -> None:
    _emit("WARNING", str(string))


def LogError(string="") -> None:
    _emit("ERROR", str(string))


_USE_CONSOLE = True
_sink = None


def use_console(enable: bool) -> None:
    global _USE_CONSOLE
    _USE_CONSOLE = enable


def set_sink(fn) -> None:
    '''设置日志接收回调 fn(level, message)，可在任意线程调用'''
    global _sink
    _sink = fn


def _emit(level, string) -> None:
    if _USE_CONSOLE:
        color = {"INFO": "\033[92m", "WARNING": "\033[93m", "ERROR": "\033[91m"}[level]
        print(f"{color}{level}:{string}\033[0m")
    if _sink is not None:
        try:
            _sink(level, string)
        except Exception:
            pass

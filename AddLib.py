import sys
import os

def add_lib():
    # 获取当前文件的目录
    current_dir = os.path.dirname(__file__)
    # 构建到lib目录的相对路径
    lib_path = os.path.join(current_dir, 'lib')

    sys.path.append(lib_path)
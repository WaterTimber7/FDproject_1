# Pyqt5/__init__.py
"""
QtWindows 主包
==========
本包包含了构建跌倒检测系统 GUI 和数据库所需的所有核心组件。
"""

# 1. 从 Windows 子包提升核心窗口类
from .Windows.LoginWindow import LoginWindow
from .Windows.RegisterWindow import RegisterWindow
from .QtWidget.LogWidget import LogWidget

# 2. 从 SQLite 子包提升核心数据库类
from .SQlite import SQLiteManager, DataValidator

# 3. 暴露子包模块本身，以便用户深入访问
from . import Windows
from . import SQlite
from . import QtWidget

# 4. 包元信息
__version__ = "1.0.0"
__author__ = "Dracaena_fragrans7"
__description__ = "PyQt5 图形界面与本地数据库集成包"

# 5. 定义公共接口：哪些名字可以通过 `from Pyqt5 import *` 导入
__all__ = [
    # 核心窗口类
    'LoginWindow',
    'RegisterWindow',
    'SQLiteManager',
    'DataValidator',
    'Windows',
    'SQlite',
    'QtWidget',
    'LogWidget',
]
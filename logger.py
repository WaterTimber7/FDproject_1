import os
import sys
import time
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal


class FileLogger:
    """文件日志记录器"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self._ensure_log_dir()
        self._setup_log_files()
        
    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _setup_log_files(self):
        """设置日志文件"""
        # 获取当前日期
        current_date = datetime.now().strftime("%Y%m%d")
        
        # 日志文件路径
        self.app_log_file = os.path.join(self.log_dir, f"app_{current_date}.log")
        self.console_log_file = os.path.join(self.log_dir, f"console_{current_date}.log")
        
        # 初始化日志文件头
        self._write_file_header()
    
    def _write_file_header(self):
        """写入文件头"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"=== 应用启动时间: {timestamp} ===\n\n"
        
        # 写入应用日志文件头
        with open(self.app_log_file, 'a', encoding='utf-8') as f:
            f.write(f"{header}")
        
        # 写入控制台日志文件头
        with open(self.console_log_file, 'a', encoding='utf-8') as f:
            f.write(f"{header}")
    
    def write_app_log(self, level: str, message: str):
        """写入应用日志"""
        # [新增] 白名单过滤：只保留包含目标检测关键字的日志
        if "确认检测到目标" not in message:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.app_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def write_console_log(self, message: str):
        """写入控制台日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.console_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


class AppLogger(QObject):
    log_signal = pyqtSignal(str, str)  # message, level
    
    def __init__(self):
        super().__init__()
        self.file_logger = FileLogger()
        self._setup_console_capture()
    
    def _setup_console_capture(self):
        """设置控制台输出捕获"""
        # 创建自定义输出流
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # 设置自定义输出流
        sys.stdout = self.ConsoleOutput(self, "STDOUT")
        sys.stderr = self.ConsoleOutput(self, "STDERR")
    
    class ConsoleOutput:
        """自定义控制台输出类"""
        
        def __init__(self, logger, stream_type):
            self.logger = logger
            self.stream_type = stream_type
            self.original_stream = sys.stdout if stream_type == "STDOUT" else sys.stderr
        
        def write(self, message):
            """写入消息"""
            if message.strip():  # 忽略空消息
                # 1. 正常输出到控制台终端
                self.original_stream.write(message)
                
                # [新增] 2. 黑名单过滤：不需要记录到 console.log 文件的冗余/隐私信息
                blacklist = [
                    "{'id':",
                    "'permission_level':",
                    "登录信息：",
                    "查询成功的用户信息"
                ]
                if any(keyword in message for keyword in blacklist):
                    return  # 命中黑名单，直接跳过文件写入
                
                # 3. 写入到控制台日志文件
                self.logger.file_logger.write_console_log(f"[{self.stream_type}] {message.rstrip()}")
        
        def flush(self):
            """刷新缓冲区"""
            self.original_stream.flush()
    
    def info(self, msg: str):
        """信息级别日志"""
        self.file_logger.write_app_log("INFO", msg)
        self.log_signal.emit(msg, "INFO")

    def error(self, msg: str):
        """错误级别日志"""
        self.file_logger.write_app_log("ERROR", msg)
        self.log_signal.emit(msg, "ERROR")

    def warn(self, msg: str):
        """警告级别日志"""
        self.file_logger.write_app_log("WARN", msg)
        self.log_signal.emit(msg, "WARN")

    def debug(self, msg: str):
        """调试级别日志"""
        self.file_logger.write_app_log("DEBUG", msg)
        self.log_signal.emit(msg, "DEBUG")
    
    def __del__(self):
        """析构函数，恢复原始输出流"""
        if hasattr(self, 'original_stdout'):
            sys.stdout = self.original_stdout
        if hasattr(self, 'original_stderr'):
            sys.stderr = self.original_stderr


# 全局唯一实例
app_logger = AppLogger()
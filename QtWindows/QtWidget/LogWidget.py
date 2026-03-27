from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from datetime import datetime


class LogWidget(QWidget):
    """
    日志输出组件
    - 支持 INFO / ERROR 等级
    - 自动滚动
    - 线程安全
    """

    # 🔒 线程安全信号（str: message, str: level）
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 文本输出框（性能优于 QTextEdit）
        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setMaximumBlockCount(1000)  # 最多保留1000行，防止内存暴涨

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)

        # 连接信号
        self.log_signal.connect(self._append_log)

        # 预定义日志颜色
        self._log_colors = {
            "INFO": QColor("#2E7D32"),    # 深绿色
            "ERROR": QColor("#C62828"),   # 深红色
            "WARN": QColor("#ED6C02"),    # 橙色
            "DEBUG": QColor("#1565C0"),   # 蓝色
        }

    # =========================
    # 对外接口（线程安全）
    # =========================

    def log_info(self, message: str):
        self.log_signal.emit(message, "INFO")

    def log_error(self, message: str):
        self.log_signal.emit(message, "ERROR")

    def log_warn(self, message: str):
        self.log_signal.emit(message, "WARN")

    def log_debug(self, message: str):
        self.log_signal.emit(message, "DEBUG")

    # =========================
    # 内部方法（主线程执行）
    # =========================

    def _append_log(self, message: str, level: str):
        """真正写入 UI（只能在主线程）"""

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)

        # 时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 字符格式
        fmt = QTextCharFormat()
        fmt.setForeground(self._log_colors.get(level, Qt.black))

        cursor.setCharFormat(fmt)
        cursor.insertText(f"[{timestamp}] [{level}] {message}\n")

        # 自动滚动到末尾
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

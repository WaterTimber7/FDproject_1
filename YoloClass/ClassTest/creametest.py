import threading
import time
import numpy as np
from typing import Optional
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap



class IntervalCamera:
    def __init__(
        self,
        source=0,
        interval=0.05,          # 0.05s 或 1s
        width=1280,
        height=720
    ):
        """
        :param source: 摄像头索引 / 视频路径 / RTSP
        :param interval: 采集时间间隔（秒）
        :param width: 输出宽度
        :param height: 输出高度
        """
        self.source = source
        self.interval = interval
        self.width = width
        self.height = height

        self.cap = None
        self.running = False

        self._frame_lock = threading.Lock()
        self._latest_frame: Optional[np.ndarray] = None

        self._thread = None

    # -------------------------
    # 启动
    # -------------------------
    def start(self):
        self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError(f"无法打开摄像头: {self.source}")

        self.running = True
        self._thread = threading.Thread(
            target=self._capture_loop, daemon=True
        )
        self._thread.start()

    # -------------------------
    # 采集线程（定时）
    # -------------------------
    def _capture_loop(self):
        while self.running:
            start = time.time()

            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (self.width, self.height))
                with self._frame_lock:
                    self._latest_frame = frame

            # 精确控制采集间隔
            elapsed = time.time() - start
            sleep_time = max(0, self.interval - elapsed)
            time.sleep(sleep_time)

    # -------------------------
    # 对外读取接口
    # -------------------------
    def read(self) -> Optional[np.ndarray]:
        """
        :return: BGR ndarray，直接可用于 YOLO / PyQt
        """
        with self._frame_lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    # -------------------------
    # 停止
    # -------------------------
    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

    def is_running(self):
        return self.running


class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interval Camera Demo")
        self.resize(800, 600)

        self.label = QLabel()
        self.label.setScaledContents(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # 摄像头：每 0.05 秒采一帧
        self.camera = IntervalCamera(source=1, interval=0.05)
        self.camera.start()

        # UI 刷新定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)   # UI 30ms 刷新一次

    def update_frame(self):
        frame = self.camera.read()
        if frame is None:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w

        qimg = QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )
        self.label.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        self.camera.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CameraWidget()
    win.show()
    sys.exit(app.exec_())


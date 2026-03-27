
import threading
import time
import numpy as np
from typing import Optional
import cv2

class IntervalCamera:
    def __init__(
        self,
        source=0,
        name=None,
        interval=1,          # 0.05s 或 1s
        width=1280,
        height=720
    ):
        """
        :param source: 摄像头索引 / 视频路径 / RTSP
        :param interval: 采集时间间隔（秒）
        :param width: 输出宽度
        :param height: 输出高度
        """
        self.name = name
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
        """
        启动摄像头，尝试多种方式打开
        """
        # 如果 source 是字符串（视频路径或 RTSP），直接打开
        if isinstance(self.source, str):
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                raise RuntimeError(f"无法打开视频源: {self.source}")
            return
        
        # 如果是数字索引，尝试多种方式打开摄像头
        # 先尝试 DSHOW（Windows 推荐）
        self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            # DSHOW 失败，尝试默认后端
            self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            # 都失败了，尝试其他后端
            backends = [
                cv2.CAP_MSMF,  # Windows Media Foundation
                cv2.CAP_V4L2,  # Linux
            ]
            for backend in backends:
                try:
                    self.cap = cv2.VideoCapture(self.source, backend)
                    if self.cap.isOpened():
                        # 测试是否能读取一帧
                        ret, _ = self.cap.read()
                        if ret:
                            break
                        else:
                            self.cap.release()
                            self.cap = None
                except:
                    if self.cap:
                        self.cap.release()
                    self.cap = None
                    continue
        
        if not self.cap or not self.cap.isOpened():
            raise RuntimeError(
                f"无法打开摄像头索引 {self.source}。\n"
            )

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


    def read(self) -> Optional[np.ndarray]:
        """
        :return: BGR ndarray，直接可用于 YOLO / PyQt
        """
        with self._frame_lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def stop(self):
        """安全停止摄像头，等待采集线程完全退出"""
        self.running = False
        
        # 等待采集线程完全退出
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        
        # 释放摄像头资源
        if self.cap:
            self.cap.release()
            self.cap = None

    def is_running(self):
        return self.running
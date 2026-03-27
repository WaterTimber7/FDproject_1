import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer


class CameraViewWidget(QWidget):
    """
    实时摄像头画面显示组件
    - 显示视频帧
    - 根据检测结果画 bbox
    - 摄像头故障时显示提示文本
    - 左上角显示摄像头名称
    """

    def __init__(self, camera, detector, camera_name: str, parent=None):
        """
        :param camera: IntervalCamera 实例
        :param detector: YOLODetector 实例
        :param camera_name: 摄像头名称
        """
        super().__init__(parent)

        self.camera = camera
        self.detector = detector
        self.camera_name = camera_name

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建摄像头名称标签（左上角）
        self.name_label = QLabel(camera_name)
        self.name_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 5px 10px;
            border-bottom-right-radius: 5px;
        """)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.name_label.setFixedHeight(30)

        # 创建图像显示容器
        self.image_container = QWidget()
        image_layout = QVBoxLayout(self.image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black; color: white; font-size: 16px;")

        # 将名称标签和图像标签添加到布局中
        image_layout.addWidget(self.name_label)
        image_layout.addWidget(self.image_label)

        main_layout.addWidget(self.image_container)

        self.last_results = []

        # 定时刷新 UI（30 FPS）
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(50)

    def update_frame(self):
        # 从摄像头读取最新帧
        try:
            frame = self.camera.read()
            if frame is None:
                # 摄像头画面丢失，显示提示文本
                self.image_label.setText("摄像头画面丢失")
                self.image_label.setPixmap(QPixmap())  # 清空图片
                return

            # 获取当前活跃的检测结果
            active_results = self.detector.get_active_results()

            # 更新显示的检测框
            self.last_results = active_results

            # 在帧上绘制检测框
            frame = self.draw_results(frame, self.last_results)
            self.show_frame(frame)
        except Exception as e:
            # 发生异常时也显示画面丢失
            self.image_label.setText("摄像头画面丢失")
            self.image_label.setPixmap(QPixmap())  # 清空图片

    def draw_results(self, frame: np.ndarray, results: list):
        """
        在 frame 上画检测框
        """
        for r in results:
            x1, y1, x2, y2 = map(int, r["bbox"])
            conf = r["confidence"]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{conf:.2f}",
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        return frame

    def show_frame(self, frame: np.ndarray):
        """
        numpy → QPixmap → QLabel
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w

        qimg = QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        ).copy()

        pixmap = QPixmap.fromImage(qimg)
        self.image_label.setPixmap(
            pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        self.image_label.setText("")  # 清空可能的提示文本
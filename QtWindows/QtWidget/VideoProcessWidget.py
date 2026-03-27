"""
视频处理组件
支持上传视频、YOLO检测、标注检测框、保存视频和播放
"""
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFileDialog, QLabel, QSlider, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
from ultralytics import YOLO
import os
import time
from datetime import datetime, timedelta
from logger import app_logger


class VideoProcessThread(QThread):
    """
    视频处理线程
    在后台处理视频，不阻塞UI
    """
    # 信号定义
    progress_updated = pyqtSignal(int)  # 处理进度 0-100
    frame_processed = pyqtSignal(np.ndarray)  # 处理后的帧
    detection_found = pyqtSignal(str, float, list, str)  # 检测结果: 时间戳, 置信度, bbox, 视频时间
    processing_finished = pyqtSignal(str)  # 处理完成，输出视频路径
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self, video_path: str, model_path: str, output_path: str = None, 
                 target_class: int = 0, conf: float = 0.7, confirm_times: int = 3):
        super().__init__()
        self.video_path = video_path
        self.model_path = model_path
        self.output_path = output_path or self._generate_output_path()
        self.target_class = target_class
        self.conf = conf
        self.confirm_times = confirm_times
        
        self.is_running = True
        self.tracks = []  # 目标跟踪列表
        self.iou_thresh = 0.2
        self.track_timeout = 2.0  # 目标消失超时时间（秒）
    
    def _generate_output_path(self):
        """生成输出视频路径"""
        base_name = os.path.splitext(os.path.basename(self.video_path))[0]
        output_dir = os.path.dirname(self.video_path) or "."
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(output_dir, f"{base_name}_detected_{timestamp}.mp4")
    
    def _iou(self, box1, box2):
        """计算两个框的IoU"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        inter_w = max(0, x2 - x1)
        inter_h = max(0, y2 - y1)
        inter_area = inter_w * inter_h
        
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union = area1 + area2 - inter_area
        return inter_area / union if union > 0 else 0
    
    def _update_tracks(self, detections, current_time):
        """更新目标跟踪列表"""
        # 标记所有track为未匹配
        for t in self.tracks:
            t["matched"] = False
        
        # 匹配检测结果
        for det in detections:
            bbox = det["bbox"]
            conf = det["confidence"]
            
            best_iou = 0
            best_track = None
            
            # 与已有track计算IoU
            for track in self.tracks:
                iou = self._iou(bbox, track["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_track = track
            
            if best_iou > self.iou_thresh:
                # 匹配成功，更新track
                best_track["bbox"] = bbox
                best_track["count"] += 1
                best_track["last_seen"] = current_time
                best_track["matched"] = True
                best_track["confidence"] = conf
            else:
                # 新目标
                self.tracks.append({
                    "bbox": bbox,
                    "confidence": conf,
                    "count": 1,
                    "last_seen": current_time,
                    "confirmed": False,
                    "matched": True
                })
        
        # 检查确认的目标
        confirmed_detections = []
        for track in self.tracks:
            if track["count"] >= self.confirm_times and not track["confirmed"]:
                track["confirmed"] = True
                confirmed_detections.append({
                    "bbox": track["bbox"],
                    "confidence": track["confidence"],
                    "timestamp": current_time
                })
        
        # 清理过期目标
        self.tracks = [
            t for t in self.tracks
            if current_time - t["last_seen"] < self.track_timeout
        ]
        
        return confirmed_detections
    
    def run(self):
        """执行视频处理"""
        try:
            # 加载模型
            model = YOLO(self.model_path)
            app_logger.info(f"YOLO模型加载完成: {self.model_path}")
            
            # 打开视频
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.error_occurred.emit(f"无法打开视频文件: {self.video_path}")
                return
            
            # 获取视频信息
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            app_logger.info(f"视频信息: {width}x{height}, {fps:.2f}fps, {total_frames}帧, {duration:.2f}秒")
            
            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            last_detect_time = 0
            detect_interval = 1.0  # 每秒检测一次
            
            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                current_time = frame_count / fps  # 当前视频时间（秒）
                
                # 每秒检测一次
                if current_time - last_detect_time >= detect_interval:
                    last_detect_time = current_time
                    
                    # YOLO检测
                    results = model(frame, conf=self.conf, verbose=False)
                    
                    detections = []
                    for r in results:
                        if r.boxes is None:
                            continue
                        for box in r.boxes:
                            cls = int(box.cls[0])
                            if cls != self.target_class:
                                continue
                            detections.append({
                                "confidence": float(box.conf[0]),
                                "bbox": box.xyxy[0].cpu().numpy().tolist()
                            })
                    
                    # 更新跟踪并获取确认的检测
                    confirmed = self._update_tracks(detections, current_time)
                    
                    # 发送确认的检测结果
                    for det in confirmed:
                        bbox = det["bbox"]
                        conf = det["confidence"]
                        # 格式化视频时间
                        video_time = self._format_time(current_time)
                        self.detection_found.emit(
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            conf,
                            bbox,
                            video_time
                        )
                
                # 在帧上绘制检测框
                frame_with_boxes = self._draw_detections(frame.copy())
                
                # 写入输出视频
                out.write(frame_with_boxes)
                
                # 发送处理后的帧（用于实时预览）
                if frame_count % int(fps) == 0:  # 每秒发送一帧用于预览
                    self.frame_processed.emit(frame_with_boxes)
                
                # 更新进度
                progress = int((frame_count / total_frames) * 100)
                self.progress_updated.emit(progress)
            
            # 释放资源
            cap.release()
            out.release()
            
            app_logger.info(f"视频处理完成，已保存到: {self.output_path}")
            self.processing_finished.emit(self.output_path)
            
        except Exception as e:
            self.error_occurred.emit(f"处理视频时出错: {str(e)}")
            app_logger.error(f"视频处理错误: {str(e)}")
    
    def _format_time(self, seconds):
        """将秒数转换为时分秒格式"""
        td = timedelta(seconds=int(seconds))
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _draw_detections(self, frame):
        """在帧上绘制检测框"""
        for track in self.tracks:
            if track["count"] >= self.confirm_times:
                x1, y1, x2, y2 = map(int, track["bbox"])
                conf = track["confidence"]
                
                # 绘制检测框
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # 绘制置信度文本
                label = f"{conf:.2f}"
                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
        
        return frame
    
    def stop(self):
        """停止处理"""
        self.is_running = False


class VideoProcessWidget(QWidget):
    """
    视频处理组件
    - 上传视频文件
    - YOLO检测（每秒一次）
    - 标注检测框
    - 保存处理后的视频
    - 播放视频（带进度条）
    """
    
    def __init__(self, model_path: str = "./YoloClass/VideoProcess/best.pt", 
                 target_class: int = 0, conf: float = 0.7, parent=None):
        super().__init__(parent)
        
        self.model_path = model_path
        self.target_class = target_class
        self.conf = conf
        
        self.video_path = None
        self.output_path = None
        self.process_thread = None
        self.cap = None
        self.current_frame_pos = 0
        self.total_frames = 0
        self.fps = 0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 顶部：按钮区域
        button_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton("上传视频")
        self.upload_btn.clicked.connect(self._upload_video)
        button_layout.addWidget(self.upload_btn)
        
        self.process_btn = QPushButton("开始处理")
        self.process_btn.clicked.connect(self._start_processing)
        self.process_btn.setEnabled(False)
        button_layout.addWidget(self.process_btn)
        
        self.save_btn = QPushButton("保存视频")
        self.save_btn.clicked.connect(self._save_video)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 视频显示区域
        self.video_label = QLabel("请上传视频文件")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white; min-height: 400px;")
        self.video_label.setScaledContents(False)
        layout.addWidget(self.video_label, stretch=1)
        
        # 视频控制区域
        control_layout = QVBoxLayout()
        
        # 进度条滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self._on_slider_changed)
        control_layout.addWidget(self.slider)
        
        # 时间标签
        time_layout = QHBoxLayout()
        self.time_label = QLabel("00:00:00 / 00:00:00")
        time_layout.addWidget(self.time_label)
        time_layout.addStretch()
        control_layout.addLayout(time_layout)
        
        # 播放控制按钮
        play_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("播放")
        self.play_btn.clicked.connect(self._toggle_play)
        self.play_btn.setEnabled(False)
        play_layout.addWidget(self.play_btn)
        
        play_layout.addStretch()
        control_layout.addLayout(play_layout)
        
        layout.addLayout(control_layout)
        
        # 播放定时器
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._update_video_frame)
        self.is_playing = False
    
    def _upload_video(self):
        """上传视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*.*)"
        )
        
        if file_path:
            self.video_path = file_path
            self.process_btn.setEnabled(True)
            app_logger.info(f"已选择视频文件: {os.path.basename(file_path)}")
            
            # 加载视频信息
            self._load_video_info()
    
    def _load_video_info(self):
        """加载视频信息"""
        if not self.video_path:
            return
        
        cap = cv2.VideoCapture(self.video_path)
        if cap.isOpened():
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setMaximum(self.total_frames - 1)
            
            # 显示第一帧
            ret, frame = cap.read()
            if ret:
                self._display_frame(frame)
            
            cap.release()
    
    def _start_processing(self):
        """开始处理视频"""
        if not self.video_path:
            QMessageBox.warning(self, "警告", "请先上传视频文件")
            return
        
        if not os.path.exists(self.model_path):
            QMessageBox.critical(self, "错误", f"模型文件不存在: {self.model_path}")
            return
        
        # 禁用按钮
        self.upload_btn.setEnabled(False)
        self.process_btn.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        app_logger.info("开始处理视频...")
        
        # 创建处理线程
        self.process_thread = VideoProcessThread(
            video_path=self.video_path,
            model_path=self.model_path,
            target_class=self.target_class,
            conf=self.conf,
            confirm_times=3
        )
        
        # 连接信号
        self.process_thread.progress_updated.connect(self._on_progress_updated)
        self.process_thread.detection_found.connect(self._on_detection_found)
        self.process_thread.processing_finished.connect(self._on_processing_finished)
        self.process_thread.error_occurred.connect(self._on_error_occurred)
        
        # 启动线程
        self.process_thread.start()
    
    def _on_progress_updated(self, progress: int):
        """更新处理进度"""
        self.progress_bar.setValue(progress)
    
    def _on_detection_found(self, timestamp: str, conf: float, bbox: list, video_time: str):
        """检测到目标"""
        x1, y1, x2, y2 = map(int, bbox)
        app_logger.info(
            f"检测到目标 | 视频时间: {video_time} | "
            f"置信度: {conf:.2f} | "
            f"位置: ({x1}, {y1}, {x2}, {y2})"
        )
    
    def _on_processing_finished(self, output_path: str):
        """处理完成"""
        self.output_path = output_path
        self.progress_bar.setVisible(False)
        self.upload_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        
        # 加载处理后的视频
        self._load_processed_video(output_path)
        
        QMessageBox.information(self, "完成", f"视频处理完成！\n已保存到: {output_path}")
    
    def _on_error_occurred(self, error_msg: str):
        """处理出错"""
        self.progress_bar.setVisible(False)
        self.upload_btn.setEnabled(True)
        self.process_btn.setEnabled(True)
        QMessageBox.critical(self, "错误", error_msg)
    
    def _load_processed_video(self, video_path: str):
        """加载处理后的视频"""
        self.cap = cv2.VideoCapture(video_path)
        if self.cap.isOpened():
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.setMaximum(self.total_frames - 1)
            self.slider.setEnabled(True)
            self.play_btn.setEnabled(True)
            
            # 显示第一帧
            self._seek_to_frame(0)
    
    def _save_video(self):
        """保存视频"""
        if not self.output_path:
            QMessageBox.warning(self, "警告", "没有可保存的视频")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存视频",
            "",
            "视频文件 (*.mp4);;所有文件 (*.*)"
        )
        
        if save_path:
            import shutil
            try:
                shutil.copy2(self.output_path, save_path)
                QMessageBox.information(self, "成功", f"视频已保存到: {save_path}")
                app_logger.info(f"视频已保存到: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def _toggle_play(self):
        """切换播放/暂停"""
        if not self.cap:
            return
        
        if self.is_playing:
            self.play_timer.stop()
            self.play_btn.setText("播放")
            self.is_playing = False
        else:
            if self.cap:
                self.play_timer.start(int(1000 / self.fps) if self.fps > 0 else 33)
                self.play_btn.setText("暂停")
                self.is_playing = True
    
    def _update_video_frame(self):
        """更新视频帧（播放时）"""
        if not self.cap:
            return
        
        ret, frame = self.cap.read()
        if ret:
            self._display_frame(frame)
            self.current_frame_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.slider.setValue(self.current_frame_pos)
            self._update_time_label()
        else:
            # 播放结束
            self.play_timer.stop()
            self.play_btn.setText("播放")
            self.is_playing = False
            self._seek_to_frame(0)
    
    def _on_slider_changed(self, value: int):
        """进度条改变"""
        if not self.is_playing:
            self._seek_to_frame(value)
    
    def _seek_to_frame(self, frame_number: int):
        """跳转到指定帧"""
        if not self.cap:
            return
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        if ret:
            self._display_frame(frame)
            self.current_frame_pos = frame_number
            self._update_time_label()
    
    def _display_frame(self, frame: np.ndarray):
        """显示帧"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        
        # 缩放以适应标签大小
        label_size = self.video_label.size()
        if label_size.width() > 0 and label_size.height() > 0:
            pixmap = pixmap.scaled(
                label_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        
        self.video_label.setPixmap(pixmap)
    
    def _update_time_label(self):
        """更新时间标签"""
        if not self.cap or self.fps == 0:
            return
        
        current_time = self.current_frame_pos / self.fps
        total_time = self.total_frames / self.fps
        
        current_str = self._format_time(current_time)
        total_str = self._format_time(total_time)
        
        self.time_label.setText(f"{current_str} / {total_str}")
    
    def _format_time(self, seconds):
        """格式化时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def closeEvent(self, event):
        """关闭时清理资源"""
        if self.process_thread and self.process_thread.isRunning():
            self.process_thread.stop()
            self.process_thread.wait()
        
        if self.cap:
            self.cap.release()
        
        event.accept()


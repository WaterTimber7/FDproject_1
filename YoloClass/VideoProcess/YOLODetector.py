import threading
import numpy as np
from ultralytics import YOLO
from datetime import datetime
from YoloClass.VideoProcess.IntervalCamera import IntervalCamera
from QtWindows.QtWidget.AlertManager import AudioAlertManager
import time
from logger import app_logger

class YOLODetector:
    """
    简化版 YOLO 实时检测器
    - 后台线程
    - 每秒检测一次
    - 单类检测
    - 仅在检测到目标时输出信息
    """
    def __init__(
        self,                 # IntervalCamera 实例
        source,
        name = None,
        model_path: str ="./YoloClass/VideoProcess/best.pt",
        interval: float = 1.0,  # 检测间隔（秒）
        conf: float = 0.25,
        device: str = "cpu",
        target_class: int = 0   # 只关心的类别 ID
    ):
        self.source = source
        self.name = name
        self.camera = IntervalCamera(source=source, name=name, interval=0.05)
        self.interval = interval
        self.conf = conf
        self.device = device
        self.target_class = target_class

        self.latest_result = []
        self.result_lock = threading.Lock()

        self.model = YOLO(model_path)
        self.running = False
        self.thread = None
        self.camera.start()

        self.tracks = []  # 多目标缓存
        self.confirm_times = 3  # 连续确认次数
        self.iou_thresh = 0.2  # IoU 阈值
        self.track_timeout = 2.0  # 目标消失时间（秒）
        self.audio_alert = AudioAlertManager()

        app_logger.info("YOLO 模型加载完成")

    def start(self):
        """启动检测线程"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._loop,
            daemon=True
        )
        self.thread.start()
        app_logger.info("YOLO 检测线程已启动")

    def stop(self):
        """停止检测线程，等待线程完全退出"""
        self.running = False
        
        # 等待检测线程完全退出
        if self.thread is not None:
            self.thread.join(timeout=3)
            self.thread = None
        
        # 确保摄像头线程也完全停止
        self.camera.stop()
        
        # 清除最新结果，防止内存访问冲突
        with self.result_lock:
            self.latest_result = []
        
        app_logger.info("YOLO 检测线程已停止")

    def _loop(self):
        """后台检测循环"""
        while self.running:
            start_time = time.time()

            frame = self.camera.read()
            if frame is not None:
                self._detect(frame)

            # 保证 1 秒一次
            sleep_time = max(0, self.interval - (time.time() - start_time))
            time.sleep(sleep_time)

    def _detect(self, frame: np.ndarray):
        """执行 YOLO 检测"""
        results = self.model(
            frame,
            conf=self.conf,
            device=self.device,
            verbose=False
        )

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

        if detections:
            self._print_result(detections)

    def _iou(self, box1, box2):
        """
        box: [x1, y1, x2, y2]
        """
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

    def _print_result(self, detections):
        now_time = time.time()

        # 先标记所有 track 为“本轮未匹配”
        for t in self.tracks:
            t["matched"] = False

        # ===== 匹配检测结果 =====
        for det in detections:
            bbox = det["bbox"]
            conf = det["confidence"]

            best_iou = 0
            best_track = None

            # 与已有 track 计算 IoU
            for track in self.tracks:
                iou = self._iou(bbox, track["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_track = track

            if best_iou > self.iou_thresh:
                # 匹配成功
                best_track["bbox"] = bbox
                best_track["count"] += 1
                best_track["last_seen"] = now_time
                best_track["matched"] = True
                best_track["confidence"] = conf
            else:
                # 新目标
                self.tracks.append({
                    "bbox": bbox,
                    "confidence": conf,
                    "count": 1,
                    "last_seen": now_time,
                    "confirmed": False,
                    "lost": False,
                    "matched": True
                })

        # ===== 输出确认目标 =====
        for track in self.tracks:
            if track["count"] >= self.confirm_times and not track["confirmed"]:
                app_logger.warn(
                    f"{self.name}确认检测到目标 | "
                )
                track["confirmed"] = True

            with self.result_lock:
                self.latest_result.append({
                    "bbox": track["bbox"],
                    "confidence": track["confidence"],
                    "timestamp": now_time
                })


        # ===== 清理过期目标 =====
        self.tracks = [
            t for t in self.tracks
            if now_time - t["last_seen"] < self.track_timeout
        ]

        if detections and any(track["confirmed"] for track in self.tracks):
            self.audio_alert.play_alert_sound()

    def get_result(self, clear: bool = True):
        with self.result_lock:
            results = self.latest_result.copy()
            if clear:
                self.latest_result.clear()
        return results
    
    def get_active_results(self):
        """
        获取当前活跃的检测结果（基于 tracks，不会因为频繁调用而清空）
        返回格式: [{"bbox": [x1, y1, x2, y2], "confidence": 0.xx, "timestamp": ...}, ...]
        """
        now_time = time.time()
        active_results = []
        
        # 遍历所有 tracks，返回仍在超时时间内的目标
        for track in self.tracks:
            if now_time - track["last_seen"] < self.track_timeout:
                active_results.append({
                    "bbox": track["bbox"],
                    "confidence": track["confidence"],
                    "timestamp": track["last_seen"]
                })
        
        return active_results


# detector = YOLODetector(
#     source=1,
#     model_path="best.pt",
#     interval=1.0,
#     conf=0.3,
#     device="cpu",
#     target_class=0   # 单类
# )
#
# detector.start()
#
# while True:
#     time.sleep(0.5)
#
#     results = detector.get_result()
#     if results:
#         for r in results:
#             print("外部获取到检测结果:", r)
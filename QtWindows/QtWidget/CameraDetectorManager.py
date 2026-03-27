"""
摄像头检测器管理器
用于创建和管理多个摄像头检测器及其画面组件
"""
from typing import List, Dict, Any, Tuple, Optional
import cv2
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from YoloClass.VideoProcess import YOLODetector
from QtWindows.QtWidget.CameraViewWidget import CameraViewWidget
from config.camera_config import CAMERA_CONFIG


class CameraPlaceholderWidget(QWidget):
    """
    摄像头占位组件，用于显示不可用的摄像头
    """

    def __init__(self, camera_index: int, camera_name: str, parent=None):
        super().__init__(parent)

        self.camera_index = camera_index
        self.camera_name = camera_name

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建名称标签（左上角）
        name_label = QLabel(camera_name)
        name_label.setStyleSheet("""
            background-color: rgba(51, 51, 51, 150);
            color: #cccccc;
            font-size: 14px;
            font-weight: bold;
            padding: 5px 10px;
            border-bottom-right-radius: 5px;
        """)
        name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        name_label.setFixedHeight(30)

        # 创建状态显示区域
        status_label = QLabel(f"摄像头不可用\n(索引 {camera_index})")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("""
            background-color: #333333;
            color: #cccccc;
            font-size: 14px;
            font-weight: bold;
            border: 2px solid #666666;
            border-radius: 5px;
            padding: 20px;
        """)

        layout.addWidget(name_label)
        layout.addWidget(status_label)


class CameraDetectorManager:
    """
    摄像头检测器管理器
    负责创建、管理和销毁多个摄像头检测器
    """

    def __init__(self, default_config: Dict[str, Any] = None):
        """
        初始化管理器

        :param default_config: 默认配置参数
        """
        # 默认配置
        self.default_config = {
            "model_path": "./YoloClass/VideoProcess/best.pt",
            "interval": 1.0,
            "conf": 0.7,
            "device": "cpu",
            "target_class": 0,
        }

        # 如果提供了自定义默认配置，则合并
        if default_config:
            self.default_config.update(default_config)

        # 存储所有检测器和画面组件
        self.detectors: List[YOLODetector] = []
        self.camera_views: List[CameraViewWidget] = []
        self.placeholder_views: List[CameraPlaceholderWidget] = []

    def create_camera(self, source: int, name: str, **kwargs) -> Tuple[
        Optional[YOLODetector], Optional[CameraViewWidget]]:
        # 合并配置：默认配置 + 用户参数
        config = {**self.default_config, **kwargs}

        try:
            # 创建检测器
            detector = YOLODetector(
                source=source,
                name=name,
                **config
            )
            detector.start()

            # 创建画面组件，传递摄像头名称
            camera_view = CameraViewWidget(
                camera=detector.camera,
                detector=detector,
                camera_name=name  # 传递摄像头名称
            )

            # 保存到列表
            self.detectors.append(detector)
            self.camera_views.append(camera_view)

            return detector, camera_view
        except Exception as e:
            # 如果摄像头打开失败，创建占位组件
            error_msg = f"创建摄像头 {name} (索引 {source}) 失败: {str(e)}"
            print(error_msg)

            # 创建占位组件
            placeholder = CameraPlaceholderWidget(source, name)
            self.placeholder_views.append(placeholder)

            return None, None

    def setup_cameras(self, camera_configs: List[Dict[str, Any]]):
        """
        批量设置多个摄像头

        :param camera_configs: 摄像头配置列表，每个配置包含 source 和 name，可选其他参数
        示例:
            [
                {"source": 0, "name": "cam0"},
                {"source": 1, "name": "cam1", "conf": 0.8},  # 可以覆盖默认配置
            ]
        """
        failed_cameras = []
        for config in camera_configs:
            # 复制配置，避免修改原配置
            config_copy = config.copy()
            source = config_copy.pop("source")
            name = config_copy.pop("name")

            try:
                detector, camera_view = self.create_camera(source=source, name=name, **config_copy)
                if detector and camera_view:
                    print(f"成功创建摄像头: {name} (索引 {source})")
                else:
                    print(f"摄像头 {name} (索引 {source}) 创建失败，已创建占位组件")
                    failed_cameras.append((name, source, "创建失败"))
            except Exception as e:
                error_msg = f"摄像头 {name} (索引 {source}) 创建失败: {str(e)}"
                print(error_msg)
                failed_cameras.append((name, source, str(e)))

        if failed_cameras:
            print(f"\n警告: {len(failed_cameras)} 个摄像头创建失败:")
            for name, source, error in failed_cameras:
                print(f"  - {name} (索引 {source}): {error}")
            print("\n提示: 如果安装了OBS虚拟摄像头插件，可能需要:")
            print("  1. 检查设备管理器中的摄像头设备")
            print("  2. 尝试使用其他摄像头索引")
            print("  3. 临时禁用OBS虚拟摄像头插件")

    def get_detectors(self) -> List[YOLODetector]:
        """获取所有检测器列表"""
        return self.detectors

    def get_camera_views(self) -> List[CameraViewWidget]:
        """获取所有摄像头画面组件列表"""
        return self.camera_views

    def get_placeholder_views(self) -> List[CameraPlaceholderWidget]:
        """获取所有占位组件列表"""
        return self.placeholder_views

    def get_all_views(self) -> List[QWidget]:
        """获取所有视图组件（包括摄像头和占位组件）"""
        all_views = []
        # 合并所有视图，保持原始顺序
        for i in range(len(self.camera_views) + len(self.placeholder_views)):
            if i < len(self.camera_views):
                all_views.append(self.camera_views[i])
            else:
                all_views.append(self.placeholder_views[i - len(self.camera_views)])
        return all_views

    def stop_all(self):
        """停止所有检测器，释放摄像头资源，并清空所有列表"""
        print("正在停止所有检测器...")
        
        # 先停止所有检测器
        for detector in self.detectors:
            try:
                detector.stop()
            except Exception as e:
                print(f"停止检测器时出错: {e}")
        
        # 彻底清空所有列表，防止旧引用导致崩溃
        self.detectors.clear()
        self.camera_views.clear()
        self.placeholder_views.clear()
        print("所有检测器已停止，列表已清空")

    def refresh_cameras(self, permission_level: int = 0, new_config: dict = None):
        """
        刷新摄像头配置，重新加载所有摄像头
        
        :param permission_level: 权限级别，用于筛选允许查看的摄像头
        :param new_config: 新的配置字典（可选），如果提供则直接使用，否则降级使用内存中的配置
        """
        print("开始刷新摄像头配置...")
        
        try:
            # 1. 安全停止所有检测器并清空列表
            self.stop_all()
            
            # 2. 直接使用传入的新配置，或者降级使用内存中的旧配置
            if new_config:
                allowed_cameras = new_config.get("permission_config", {}).get(permission_level, [])
                names_dict = new_config.get("camera_names", {})
                print(f"使用传入的新配置，权限级别 {permission_level} 允许查看的摄像头: {allowed_cameras}")
            else:
                # 降级：重新加载配置文件
                import importlib
                import config.camera_config as camera_config
                importlib.reload(camera_config)
                allowed_cameras = camera_config.CAMERA_CONFIG["permission_config"].get(permission_level, [])
                names_dict = camera_config.CAMERA_CONFIG["camera_names"]
                print(f"降级使用文件配置，权限级别 {permission_level} 允许查看的摄像头: {allowed_cameras}")

            if len(allowed_cameras) == 0:
                print("当前权限级别没有可查看的摄像头")
                return

            # 3. 重新创建摄像头配置
            camera_configs = []
            for source in allowed_cameras:
                camera_name = names_dict.get(source, f"cam{source}")
                camera_configs.append({"source": source, "name": camera_name})

            # 4. 重新设置摄像头
            if camera_configs:
                self.setup_cameras(camera_configs)
                print(f"摄像头刷新完成，共加载 {len(camera_configs)} 个摄像头配置")
            else:
                print("没有摄像头配置需要加载")
                
        except Exception as e:
            print(f"刷新摄像头配置时出错: {e}")
            import traceback
            traceback.print_exc()

    def get_camera_configs(self, permission_level: int = 0) -> List[Dict[str, Any]]:
        """
        获取当前权限级别下的摄像头配置列表
        
        :param permission_level: 权限级别
        :return: 摄像头配置列表
        """
        allowed_cameras = CAMERA_CONFIG["permission_config"].get(permission_level, [])
        camera_configs = []
        
        for source in allowed_cameras:
            camera_name = CAMERA_CONFIG["camera_names"].get(source, f"cam{source}")
            camera_configs.append({"source": source, "name": camera_name})
            
        return camera_configs

    @staticmethod
    def find_available_cameras(max_index: int = 10) -> List[int]:
        """
        检测可用的摄像头索引

        :param max_index: 最大检测索引（默认检测 0-9）
        :return: 可用摄像头索引列表
        """
        available = []
        for i in range(max_index):
            cap = None
            try:
                # 尝试多种方式打开
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    cap = cv2.VideoCapture(i)

                if cap.isOpened():
                    # 尝试读取一帧来确认摄像头真的可用
                    ret, _ = cap.read()
                    if ret:
                        available.append(i)
            except:
                pass
            finally:
                if cap:
                    cap.release()

        return available

    def __del__(self):
        """析构函数，确保资源被释放"""
        self.stop_all()
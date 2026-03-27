import sys
import os
import math

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,  # 新增网格布局
    QPushButton,
    QStackedWidget,
    QLabel,
    QScrollArea,  # 新增滚动区域
)
from PyQt5.QtCore import Qt
from QtWindows.QtWidget import LogWidget, CameraDetectorManager, VideoProcessWidget
from logger import app_logger
# 导入配置文件
from config.camera_config import CAMERA_CONFIG


class MainWindow(QMainWindow):
    def __init__(self, permission_level: int = 0):
        """
        初始化主窗口

        :param permission_level: 用户权限级别（从登录界面传入）
        """
        super().__init__()
        print(f"打开主窗口成功，权限级别: {permission_level}")

        # 保存权限级别
        self.permission_level = permission_level

        # ====== 初始化摄像头管理器 ======
        self.camera_manager = CameraDetectorManager()
        self._setup_cameras()

        # ====== 初始化界面 ======
        self._setup_ui()

    def _setup_cameras(self):
        """
        批量设置多个摄像头
        根据配置文件和权限级别选择要使用的摄像头
        即使摄像头不可用，也会创建占位组件
        """
        # 检测所有可能的摄像头（索引0-9）
        available_cameras = CameraDetectorManager.find_available_cameras(max_index=9)
        app_logger.info(f"检测到可用摄像头索引: {available_cameras}")

        # 根据权限级别获取允许查看的摄像头索引
        allowed_cameras = CAMERA_CONFIG["permission_config"].get(self.permission_level, [])
        app_logger.info(f"权限级别 {self.permission_level} 允许查看的摄像头: {allowed_cameras}")

        if len(allowed_cameras) == 0:
            app_logger.warn("当前权限级别没有可查看的摄像头")
            return

        # 配置要使用的摄像头（包括不可用的摄像头，会创建占位组件）
        camera_configs = []

        for source in allowed_cameras:
            # 使用配置文件中的摄像头名称
            camera_name = CAMERA_CONFIG["camera_names"].get(source, f"cam{source}")

            if source in available_cameras:
                print(f"添加可用摄像头: {camera_name} (索引 {source})")
            else:
                print(f"添加不可用摄像头占位: {camera_name} (索引 {source})")

            camera_configs.append({"source": source, "name": camera_name})

        if camera_configs:
            self.camera_manager.setup_cameras(camera_configs)

    def refresh_camera_views(self, new_config: dict = None):
        """
        刷新摄像头视图
        重新加载配置文件并更新显示界面
        
        :param new_config: 新的配置字典（可选），如果提供则直接使用，否则从文件重新加载
        """
        # 防御性检查：确保 UI 完全初始化
        if not hasattr(self, 'stacked_widget') or not hasattr(self, 'camera_manager'):
            print("UI 尚未完全初始化，跳过刷新")
            return
        
        if not hasattr(self, 'camera_container'):
            print("camera_container 尚未创建，跳过刷新")
            return
        
        print("开始刷新摄像头视图...")
        app_logger.info("开始刷新摄像头视图")
        
        try:
            # 1. 刷新摄像头管理器中的配置（包含安全的线程停止）
            self.camera_manager.refresh_cameras(self.permission_level, new_config)
            
            # 2. 获取新的视图组件列表
            all_views = self.camera_manager.get_all_views()
            
            # 3. 安全移除旧的摄像头容器
            if hasattr(self, 'camera_container') and self.camera_container is not None:
                # 先从堆叠窗口中移除
                self.stacked_widget.removeWidget(self.camera_container)
                # 使用 deleteLater 安全释放 C++ 内存
                self.camera_container.deleteLater()
            
            # 4. 创建新的摄像头容器
            self.camera_container = QWidget()
            
            if len(all_views) == 0:
                # 如果没有视图组件，显示提示信息
                camera_container_layout = QVBoxLayout(self.camera_container)
                no_camera_label = QLabel("当前权限级别没有可查看的摄像头")
                no_camera_label.setAlignment(Qt.AlignCenter)
                no_camera_label.setStyleSheet("color: red; font-size: 16px;")
                camera_container_layout.addWidget(no_camera_label)
            else:
                # 使用网格布局显示所有视图组件
                grid_layout = QGridLayout(self.camera_container)
                grid_layout.setContentsMargins(5, 5, 5, 5)
                grid_layout.setSpacing(5)

                # 计算网格的行数和列数（最多3列）
                num_views = len(all_views)
                max_cols = min(3, num_views)  # 最多3列
                rows = math.ceil(num_views / max_cols)

                # 将视图组件添加到网格中
                for i, view in enumerate(all_views):
                    row = i // max_cols
                    col = i % max_cols
                    grid_layout.addWidget(view, row, col)

            # 5. 将新的容器添加到堆叠窗口中
            self.stacked_widget.insertWidget(0, self.camera_container)
            
            # 6. 保持当前显示模式为摄像头检测
            if self.stacked_widget.currentIndex() == 0:
                self.stacked_widget.setCurrentIndex(0)
            
            print(f"摄像头视图刷新完成，共显示 {len(all_views)} 个摄像头")
            app_logger.info(f"摄像头视图刷新完成，共显示 {len(all_views)} 个摄像头")
            
        except Exception as e:
            print(f"刷新摄像头视图时出错: {e}")
            import traceback
            traceback.print_exc()
            app_logger.error(f"刷新摄像头视图时出错: {e}")

    def _setup_ui(self):
        """
        设置用户界面布局
        """
        # 日志组件（共用一个）
        self.log_widget = LogWidget()
        app_logger.log_signal.connect(self.log_widget._append_log)

        # ====== 窗口和布局 ======
        self.setWindowTitle("检测系统主窗口")
        self.resize(1400, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局：上下布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # 上半部分：左右布局
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        # 左侧：按钮区域（占1/4）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(10, 10, 10, 10)

        # 摄像头检测按钮
        self.camera_btn = QPushButton("摄像头检测")
        self.camera_btn.setMinimumHeight(50)
        self.camera_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
        """)
        self.camera_btn.clicked.connect(self._show_camera_view)
        left_layout.addWidget(self.camera_btn)

        # 视频处理按钮
        self.video_btn = QPushButton("视频处理")
        self.video_btn.setMinimumHeight(50)
        self.video_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.video_btn.clicked.connect(self._show_video_view)
        left_layout.addWidget(self.video_btn)
        left_layout.addStretch()

        top_layout.addWidget(left_widget, stretch=1)

        # 右侧：内容切换区域（占3/4）
        self.stacked_widget = QStackedWidget()

        # 创建摄像头检测视图容器
        self.camera_container = QWidget()

        # 获取所有视图组件（包括摄像头和占位组件）
        all_views = self.camera_manager.get_all_views()

        if len(all_views) == 0:
            # 如果没有视图组件，显示提示信息
            camera_container_layout = QVBoxLayout(self.camera_container)
            no_camera_label = QLabel("当前权限级别没有可查看的摄像头")
            no_camera_label.setAlignment(Qt.AlignCenter)
            no_camera_label.setStyleSheet("color: red; font-size: 16px;")
            camera_container_layout.addWidget(no_camera_label)
        else:
            # 使用网格布局显示所有视图组件
            grid_layout = QGridLayout(self.camera_container)
            grid_layout.setContentsMargins(5, 5, 5, 5)
            grid_layout.setSpacing(5)

            # 计算网格的行数和列数（最多3列）
            num_views = len(all_views)
            max_cols = min(3, num_views)  # 最多3列
            rows = math.ceil(num_views / max_cols)

            # 将视图组件添加到网格中
            for i, view in enumerate(all_views):
                row = i // max_cols
                col = i % max_cols
                grid_layout.addWidget(view, row, col)

        # 创建视频处理组件
        self.video_widget = VideoProcessWidget(
            model_path="./YoloClass/VideoProcess/best.pt",
            target_class=0,
            conf=0.7
        )

        # 添加到堆叠窗口
        self.stacked_widget.addWidget(self.camera_container)  # 索引 0
        self.stacked_widget.addWidget(self.video_widget)  # 索引 1

        # 默认显示摄像头检测
        self.stacked_widget.setCurrentIndex(0)
        self._update_button_styles(0)

        top_layout.addWidget(self.stacked_widget, stretch=3)

        main_layout.addLayout(top_layout, stretch=3)

        # 下半部分：日志区域
        main_layout.addWidget(self.log_widget, stretch=1)

    def _show_camera_view(self):
        """显示摄像头检测视图"""
        print(f"切换到摄像头检测模式，当前索引: {self.stacked_widget.currentIndex()}")
        self.stacked_widget.setCurrentIndex(0)
        self._update_button_styles(0)
        app_logger.info("切换到摄像头检测模式")
        print(f"切换后索引: {self.stacked_widget.currentIndex()}")

    def _show_video_view(self):
        """显示视频处理视图"""
        print(f"切换到视频处理模式，当前索引: {self.stacked_widget.currentIndex()}")
        self.stacked_widget.setCurrentIndex(1)
        self._update_button_styles(1)
        app_logger.info("切换到视频处理模式")
        print(f"切换后索引: {self.stacked_widget.currentIndex()}")

    def _update_button_styles(self, active_index: int):
        """更新按钮样式，高亮当前激活的按钮"""
        if active_index == 0:
            # 摄像头检测激活
            self.camera_btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #2E7D32;
                    color: white;
                    border-radius: 5px;
                    border: 3px solid #1B5E20;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #388e3c;
                }
            """)
            self.video_btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #2196F3;
                    color: white;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
            """)
        else:
            # 视频处理激活
            self.video_btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #1565C0;
                    color: white;
                    border-radius: 5px;
                    border: 3px solid #0D47A1;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
            """)
            self.camera_btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #388e3c;
                }
            """)

    def closeEvent(self, event):
        """
        关闭窗口时，主动停止所有检测器，释放摄像头资源
        """
        try:
            self.camera_manager.stop_all()
        finally:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
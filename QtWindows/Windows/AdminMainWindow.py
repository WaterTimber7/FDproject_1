import sys
from PyQt5.QtWidgets import QPushButton, QApplication
from QtWindows.Windows.MainWindo import MainWindow
from QtWindows.QtWidget.UserManagementWidget import UserManagementWidget
from QtWindows.QtWidget.CameraConfigWidget import CameraConfigWidget
from logger import app_logger


class AdminMainWindow(MainWindow):
    def __init__(self, permission_level: int = 5):
        super().__init__(permission_level)
        self.setWindowTitle("检测系统主窗口 (管理员模式)")
        self._setup_admin_ui()

    def _setup_admin_ui(self):
        # 1. 获取左侧布局并添加按钮
        left_widget = self.video_btn.parentWidget()
        left_layout = left_widget.layout()

        # 创建用户管理按钮
        self.user_manage_btn = QPushButton("用户管理")
        self.user_manage_btn.setMinimumHeight(50)
        self.user_manage_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #9C27B0;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
        """)
        self.user_manage_btn.clicked.connect(self._show_user_management)

        # 创建配置管理按钮
        self.config_btn = QPushButton("配置管理")
        self.config_btn.setMinimumHeight(50)
        self.config_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #FF9800;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
        """)
        self.config_btn.clicked.connect(self._show_config_management)

        # 插入到倒数第二个位置（最后一个是 stretch）
        count = left_layout.count()
        left_layout.insertWidget(count - 1, self.config_btn)
        left_layout.insertWidget(count - 1, self.user_manage_btn)

        # 2. 添加用户管理组件到 stacked_widget
        self.user_manage_widget = UserManagementWidget()
        self.stacked_widget.addWidget(self.user_manage_widget)

        # 3. 添加配置管理组件到 stacked_widget
        self.config_widget = CameraConfigWidget()
        self.stacked_widget.addWidget(self.config_widget)

    def _show_user_management(self):
        """显示用户管理界面"""
        print(f"切换到用户管理模式")
        self.stacked_widget.setCurrentWidget(self.user_manage_widget)
        self._update_button_styles(2)
        app_logger.info("切换到用户管理模式")

    def _show_config_management(self):
        """显示配置管理界面"""
        print(f"切换到配置管理模式")
        self.stacked_widget.setCurrentWidget(self.config_widget)
        self._update_button_styles(3)
        app_logger.info("切换到配置管理模式")

    def _update_button_styles(self, active_index: int):
        super()._update_button_styles(active_index)

        # 检查按钮是否已经创建
        if not hasattr(self, 'user_manage_btn') or not hasattr(self, 'config_btn'):
            return

        """重写以支持四个按钮"""
        # 定义基础样式
        base_style = """
            QPushButton {{
                font-size: 14px;
                font-weight: bold;
                background-color: {color};
                color: white;
                border-radius: 5px;
                {border}
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """

        # 颜色配置
        colors = {
            'camera': {'color': '#4CAF50', 'hover': '#45a049', 'pressed': '#388e3c', 'active': '#2E7D32',
                       'border': '#1B5E20'},
            'video': {'color': '#2196F3', 'hover': '#1976D2', 'pressed': '#1565C0', 'active': '#1565C0',
                      'border': '#0D47A1'},
            'admin': {'color': '#9C27B0', 'hover': '#7B1FA2', 'pressed': '#6A1B9A', 'active': '#7B1FA2',
                      'border': '#4A148C'},
            'config': {'color': '#FF9800', 'hover': '#F57C00', 'pressed': '#EF6C00', 'active': '#F57C00',
                       'border': '#E65100'}
        }

        def get_style(key, is_active):
            c = colors[key]
            bg = c['active'] if is_active else c['color']
            border = f"border: 3px solid {c['border']};" if is_active else ""
            return base_style.format(
                color=bg,
                hover_color=c['hover'],
                pressed_color=c['pressed'],
                border=border
            )

        self.camera_btn.setStyleSheet(get_style('camera', active_index == 0))
        self.video_btn.setStyleSheet(get_style('video', active_index == 1))
        self.user_manage_btn.setStyleSheet(get_style('admin', active_index == 2))
        self.config_btn.setStyleSheet(get_style('config', active_index == 3))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = AdminMainWindow()
    window.show()

    sys.exit(app.exec_())
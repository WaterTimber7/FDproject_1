import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class DynamicTabWindow(QMainWindow):
    """
    可变标签页窗口类
    根据传入的tab_count参数创建不同数量的标签页
    """

    def __init__(self, tab_count=3, parent=None):
        """
        初始化窗口

        参数:
            tab_count (int): 要打开的标签页数量，范围1-3
                1: 只打开第一个标签页
                2: 打开前两个标签页
                3: 打开全部三个标签页
        """
        super().__init__(parent)

        # 验证参数有效性
        if tab_count not in [1, 2, 3]:
            raise ValueError("tab_count 必须是 1, 2 或 3")

        self.tab_count = tab_count
        self.tabs = []  # 存储标签页引用
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(f"可变标签页窗口 (显示 {self.tab_count} 个标签页)")
        self.setGeometry(100, 100, 900, 600)

        # 设置应用图标
        self.setWindowIcon(QIcon.fromTheme("applications-system"))

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 创建标题标签
        title_label = QLabel(f"动态标签页窗口 - 显示 {self.tab_count} 个标签页")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
        """)
        main_layout.addWidget(title_label)

        # 创建标签页控件
        self.tab_widget = QTabWidget()

        # 根据tab_count创建相应数量的标签页
        self.create_tabs()

        # 将标签页控件添加到主布局
        main_layout.addWidget(self.tab_widget, 1)  # 1表示拉伸因子

        # 创建控制面板
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage(f"已创建 {self.tab_count} 个标签页")

        # 设置初始焦点
        self.setFocus()

    def create_tabs(self):
        """根据tab_count创建标签页"""
        # 清空现有标签页
        self.tab_widget.clear()
        self.tabs = []

        # 预定义的标签页配置
        tab_configs = [
            {
                "title": "标签页 1 - 系统信息",
                "color": "#e3f2fd",  # 浅蓝色
                "content": "系统信息页面",
                "icon": QStyle.SP_ComputerIcon,
                "widget_type": "system_info"
            },
            {
                "title": "标签页 2 - 文件管理",
                "color": "#f3e5f5",  # 浅紫色
                "content": "文件管理页面",
                "icon": QStyle.SP_DirIcon,
                "widget_type": "file_manager"
            },
            {
                "title": "标签页 3 - 设置选项",
                "color": "#e8f5e9",  # 浅绿色
                "content": "设置选项页面",
                "icon": QStyle.SP_FileDialogInfoView,
                "widget_type": "settings"
            }
        ]

        # 根据tab_count创建相应数量的标签页
        for i in range(self.tab_count):
            config = tab_configs[i]

            # 创建标签页内容
            tab_widget = self.create_tab_content(config, i + 1)
            self.tabs.append(tab_widget)

            # 添加标签页到标签控件
            if config.get("icon"):
                icon = self.style().standardIcon(config["icon"])
                self.tab_widget.addTab(tab_widget, icon, config["title"])
            else:
                self.tab_widget.addTab(tab_widget, config["title"])

    def create_tab_content(self, config, tab_index):
        """创建标签页内容"""
        # 创建主widget
        widget = QWidget()

        # 设置背景颜色
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {config["color"]};
                border-radius: 5px;
            }}
        """)

        # 创建垂直布局
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 添加标题
        title = QLabel(config["title"])
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #bdc3c7;")
        layout.addWidget(line)

        # 根据标签页类型创建不同的内容
        if config["widget_type"] == "system_info":
            content = self.create_system_info_tab(tab_index)
        elif config["widget_type"] == "file_manager":
            content = self.create_file_manager_tab(tab_index)
        elif config["widget_type"] == "settings":
            content = self.create_settings_tab(tab_index)
        else:
            content = QLabel(config["content"])
            content.setWordWrap(True)
            content.setAlignment(Qt.AlignCenter)

        layout.addWidget(content, 1)  # 1表示拉伸因子

        # 添加底部信息
        bottom_label = QLabel(f"这是第 {tab_index} 个标签页，共 {self.tab_count} 个")
        bottom_label.setAlignment(Qt.AlignRight)
        bottom_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(bottom_label)

        return widget

    def create_system_info_tab(self, tab_index):
        """创建系统信息标签页内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 系统信息列表
        info_list = QListWidget()

        # 添加模拟的系统信息
        system_info = [
            f"标签页 {tab_index}: 系统信息",
            f"操作系统: Windows 10",
            f"处理器: Intel Core i7",
            f"内存: 16 GB",
            f"磁盘空间: 512 GB SSD",
            f"当前用户: Administrator",
            f"IP地址: 192.168.1.{tab_index}",
            f"最后启动: 2023-10-{tab_index:02d} 08:00"
        ]

        for info in system_info:
            item = QListWidgetItem(info)
            info_list.addItem(item)

        layout.addWidget(info_list)

        # 添加刷新按钮
        refresh_btn = QPushButton("刷新系统信息")
        refresh_btn.clicked.connect(lambda: self.refresh_system_info(tab_index))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(refresh_btn)

        return widget

    def create_file_manager_tab(self, tab_index):
        """创建文件管理标签页内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 文件列表
        file_list = QListWidget()

        # 添加模拟的文件列表
        files = [
            f"文档_{tab_index}_1.txt",
            f"图片_{tab_index}_1.jpg",
            f"报告_{tab_index}.pdf",
            f"数据_{tab_index}.csv",
            f"配置_{tab_index}.ini",
            f"日志_{tab_index}.log"
        ]

        for file in files:
            item = QListWidgetItem(file)
            file_list.addItem(item)

        layout.addWidget(file_list)

        # 添加文件操作按钮
        btn_layout = QHBoxLayout()

        open_btn = QPushButton("打开")
        delete_btn = QPushButton("删除")
        rename_btn = QPushButton("重命名")

        open_btn.clicked.connect(lambda: self.open_file(tab_index))
        delete_btn.clicked.connect(lambda: self.delete_file(tab_index))
        rename_btn.clicked.connect(lambda: self.rename_file(tab_index))

        for btn in [open_btn, delete_btn, rename_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        return widget

    def create_settings_tab(self, tab_index):
        """创建设置标签页内容"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 创建表单布局
        form_layout = QFormLayout()

        # 用户名输入
        username_edit = QLineEdit()
        username_edit.setPlaceholderText(f"请输入用户名_{tab_index}")
        form_layout.addRow(f"用户名 {tab_index}:", username_edit)

        # 主题选择
        theme_combo = QComboBox()
        theme_combo.addItems(["浅色主题", "深色主题", "自动主题"])
        form_layout.addRow(f"主题 {tab_index}:", theme_combo)

        # 音量控制
        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(70)
        form_layout.addRow(f"音量 {tab_index}:", volume_slider)

        # 启用复选框
        enable_check = QCheckBox(f"启用功能 {tab_index}")
        enable_check.setChecked(True)
        form_layout.addRow(f"启用:", enable_check)

        layout.addLayout(form_layout)

        # 添加设置操作按钮
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("保存设置")
        reset_btn = QPushButton("重置设置")

        save_btn.clicked.connect(lambda: self.save_settings(tab_index))
        reset_btn.clicked.connect(lambda: self.reset_settings(tab_index))

        for btn in [save_btn, reset_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        return widget

    def create_control_panel(self):
        """创建控制面板"""
        panel = QGroupBox("标签页控制")
        layout = QHBoxLayout()

        # 创建标签页数量选择器
        layout.addWidget(QLabel("标签页数量:"))

        self.tab_count_combo = QComboBox()
        self.tab_count_combo.addItems(["1个标签页", "2个标签页", "3个标签页"])
        self.tab_count_combo.setCurrentIndex(self.tab_count - 1)
        self.tab_count_combo.currentIndexChanged.connect(self.change_tab_count)
        layout.addWidget(self.tab_count_combo)

        layout.addStretch()

        # 添加刷新按钮
        refresh_btn = QPushButton("刷新标签页")
        refresh_btn.clicked.connect(self.refresh_tabs)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(refresh_btn)

        # 添加关闭所有标签页按钮
        close_all_btn = QPushButton("关闭所有")
        close_all_btn.clicked.connect(self.close_all_tabs)
        close_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(close_all_btn)

        panel.setLayout(layout)
        return panel

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        new_window_action = QAction("新建窗口", self)
        new_window_action.setShortcut("Ctrl+N")
        new_window_action.triggered.connect(self.new_window)
        file_menu.addAction(new_window_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        # 标签页数量子菜单
        tab_count_menu = view_menu.addMenu("标签页数量")

        for i in range(1, 4):
            action = QAction(f"{i} 个标签页", self)
            action.setCheckable(True)
            action.setChecked(i == self.tab_count)
            action.triggered.connect(lambda checked, count=i: self.set_tab_count(count))
            tab_count_menu.addAction(action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def change_tab_count(self, index):
        """改变标签页数量"""
        new_count = index + 1  # 索引从0开始，数量从1开始
        if new_count != self.tab_count:
            self.tab_count = new_count
            self.refresh_tabs()

    def set_tab_count(self, count):
        """设置标签页数量"""
        if count != self.tab_count:
            self.tab_count = count
            self.tab_count_combo.setCurrentIndex(count - 1)
            self.refresh_tabs()

    def refresh_tabs(self):
        """刷新标签页"""
        self.create_tabs()
        self.setWindowTitle(f"可变标签页窗口 (显示 {self.tab_count} 个标签页)")
        self.status_bar.showMessage(f"已刷新，当前显示 {self.tab_count} 个标签页", 3000)

    def close_all_tabs(self):
        """关闭所有标签页"""
        reply = QMessageBox.question(
            self, "确认关闭",
            "确定要关闭所有标签页吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.tab_widget.clear()
            self.tabs = []
            self.status_bar.showMessage("所有标签页已关闭", 3000)

    def new_window(self):
        """创建新窗口"""
        # 询问要创建的标签页数量
        count, ok = QInputDialog.getInt(
            self, "新建窗口",
            "请输入标签页数量 (1-3):",
            self.tab_count, 1, 3, 1
        )

        if ok:
            # 创建新窗口
            new_window = DynamicTabWindow(tab_count=count)
            new_window.show()
            new_window.move(self.x() + 30, self.y() + 30)
            self.status_bar.showMessage(f"已创建新窗口，显示 {count} 个标签页", 3000)

    def refresh_system_info(self, tab_index):
        """刷新系统信息"""
        QMessageBox.information(
            self, "系统信息",
            f"标签页 {tab_index} 的系统信息已刷新"
        )
        self.status_bar.showMessage(f"标签页 {tab_index} 的系统信息已刷新", 2000)

    def open_file(self, tab_index):
        """打开文件"""
        QMessageBox.information(
            self, "打开文件",
            f"打开标签页 {tab_index} 的文件"
        )

    def delete_file(self, tab_index):
        """删除文件"""
        reply = QMessageBox.question(
            self, "删除文件",
            f"确定要删除标签页 {tab_index} 中的文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.status_bar.showMessage(f"标签页 {tab_index} 的文件已删除", 2000)

    def rename_file(self, tab_index):
        """重命名文件"""
        QMessageBox.information(
            self, "重命名文件",
            f"重命名标签页 {tab_index} 的文件"
        )

    def save_settings(self, tab_index):
        """保存设置"""
        self.status_bar.showMessage(f"标签页 {tab_index} 的设置已保存", 2000)

    def reset_settings(self, tab_index):
        """重置设置"""
        reply = QMessageBox.question(
            self, "重置设置",
            f"确定要重置标签页 {tab_index} 的设置吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.status_bar.showMessage(f"标签页 {tab_index} 的设置已重置", 2000)

    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <h3>可变标签页窗口</h3>
        <p>这是一个可变标签页窗口演示程序。</p>
        <p><b>功能特点：</b></p>
        <ul>
            <li>可以根据传入的参数创建不同数量的标签页（1-3个）</li>
            <li>每个标签页都有不同的功能和样式</li>
            <li>可以动态改变标签页数量</li>
            <li>支持创建多个窗口实例</li>
        </ul>
        <p><b>使用方法：</b></p>
        <ol>
            <li>初始化时传入 tab_count 参数决定标签页数量</li>
            <li>使用控制面板可以动态改变标签页数量</li>
            <li>可以通过菜单栏创建新的窗口实例</li>
        </ol>
        <p>PyQt5 可变标签页演示程序</p>
        """

        QMessageBox.about(self, "关于", about_text)

    def closeEvent(self, event):
        """关闭窗口时的事件处理"""
        reply = QMessageBox.question(
            self, "确认退出",
            "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """主函数，演示不同参数创建不同窗口"""
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle('Fusion')

    # 设置全局字体
    font = QFont("微软雅黑", 10)
    app.setFont(font)

    # 演示创建不同参数窗口的方法
    print("创建可变标签页窗口演示")
    print("=" * 50)

    # 创建3个不同参数的窗口
    window1 = DynamicTabWindow(tab_count=1)
    window1.setWindowTitle("窗口1 - 1个标签页")
    window1.move(100, 100)
    window1.show()

    window2 = DynamicTabWindow(tab_count=2)
    window2.setWindowTitle("窗口2 - 2个标签页")
    window2.move(450, 100)
    window2.show()

    window3 = DynamicTabWindow(tab_count=3)
    window3.setWindowTitle("窗口3 - 3个标签页")
    window3.move(800, 100)
    window3.show()

    # 也可以从命令行参数获取
    if len(sys.argv) > 1:
        try:
            tab_count = int(sys.argv[1])
            if tab_count in [1, 2, 3]:
                window_cmd = DynamicTabWindow(tab_count=tab_count)
                window_cmd.setWindowTitle(f"命令行窗口 - {tab_count}个标签页")
                window_cmd.move(1150, 100)
                window_cmd.show()
                print(f"已从命令行参数创建窗口，标签页数量: {tab_count}")
        except ValueError:
            print(f"无效的命令行参数: {sys.argv[1]}，请使用 1, 2 或 3")

    print("=" * 50)
    print("已创建3个窗口，分别显示1、2、3个标签页")

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
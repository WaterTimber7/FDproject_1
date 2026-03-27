import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ComplexWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        # 1. 基本窗口设置
        self.setWindowTitle("复杂窗口示例")
        self.setGeometry(100, 50, 900, 700)

        # 2. 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 3. 创建主布局
        main_layout = QVBoxLayout(central_widget)  # 直接将布局传给widget

        # 4. 创建顶部工具栏区域
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)

        # 5. 创建中部内容区域（使用分割器）
        splitter = self.create_content_area()
        main_layout.addWidget(splitter, 1)  # 1表示拉伸因子

        # 6. 创建底部状态区域
        status_area = self.create_status_area()
        main_layout.addWidget(status_area)

        # 7. 创建菜单栏
        self.create_menubar()

        # 8. 创建状态栏
        self.statusBar().showMessage("就绪")

    def create_toolbar(self):
        """创建工具栏区域"""
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)

        # 添加工具按钮
        tools = ["新建", "打开", "保存", "剪切", "复制", "粘贴"]
        for tool in tools:
            btn = QPushButton(tool)
            btn.clicked.connect(lambda checked, t=tool: self.on_tool_clicked(t))
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()  # 添加弹簧

        # 添加搜索框
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("搜索...")
        search_edit.setMaximumWidth(200)
        toolbar_layout.addWidget(search_edit)

        return toolbar_widget

    def create_content_area(self):
        """创建内容区域（使用QSplitter）"""
        splitter = QSplitter(Qt.Horizontal)

        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("左侧面板"))
        left_layout.addWidget(QTextEdit())
        left_layout.addWidget(QPushButton("左侧按钮"))

        # 右侧面板（使用选项卡）
        right_tab = QTabWidget()
        right_tab.addTab(QTextEdit(), "选项卡1")
        right_tab.addTab(QTableWidget(5, 3), "选项卡2")
        right_tab.addTab(QListWidget(), "选项卡3")

        splitter.addWidget(left_panel)
        splitter.addWidget(right_tab)
        splitter.setSizes([300, 600])  # 设置初始大小

        return splitter

    def create_status_area(self):
        """创建状态区域"""
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(50)
        status_layout.addWidget(self.progress_bar)

        # 状态标签
        status_layout.addStretch()
        self.status_label = QLabel("状态: 正常")
        status_layout.addWidget(self.status_label)

        return status_widget

    def create_menubar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction("新建(&N)", self.on_new, "Ctrl+N")
        file_menu.addAction("打开(&O)...", self.on_open, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("退出(&X)", self.close, "Ctrl+Q")

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        edit_menu.addAction("撤销(&U)", self.on_undo, "Ctrl+Z")
        edit_menu.addAction("重做(&R)", self.on_redo, "Ctrl+Y")

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        help_menu.addAction("关于(&A)...", self.on_about)

    def on_tool_clicked(self, tool_name):
        """工具栏按钮点击事件"""
        self.statusBar().showMessage(f"点击了 {tool_name} 工具")
        print(f"工具点击: {tool_name}")

    def on_new(self):
        self.statusBar().showMessage("创建新文件")

    def on_open(self):
        self.statusBar().showMessage("打开文件")

    def on_undo(self):
        self.statusBar().showMessage("撤销操作")

    def on_redo(self):
        self.statusBar().showMessage("重做操作")

    def on_about(self):
        QMessageBox.information(self, "关于", "这是一个复杂的PyQt5窗口示例")

    def closeEvent(self, event):
        """重写关闭事件"""
        reply = QMessageBox.question(self, '确认退出',
                                     '确定要退出吗？',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """主函数"""
    # 创建应用实例
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    # 设置样式表
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QProgressBar {
            border: 1px solid #ccc;
            border-radius: 3px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 3px;
        }
    """)

    # 创建并显示窗口
    window = ComplexWindow()
    window.show()

    # 进入主事件循环
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
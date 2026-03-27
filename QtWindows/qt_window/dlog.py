import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置主窗口
        self.setWindowTitle("PyQt5窗口类演示")
        self.setGeometry(100, 100, 800, 600)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建布局
        layout = QVBoxLayout()

        # 添加各种按钮来演示不同的窗口类
        buttons = [
            ("显示消息对话框", self.show_message_box),
            ("打开文件对话框", self.show_file_dialog),
            ("显示输入对话框", self.show_input_dialog),
            ("选择颜色", self.show_color_dialog),
            ("选择字体", self.show_font_dialog),
            ("显示进度对话框", self.show_progress_dialog),
            ("启动向导", self.show_wizard),
            ("打开独立窗口", self.open_standalone_window),
            ("显示自定义对话框", self.show_custom_dialog),
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        layout.addStretch()
        central_widget.setLayout(layout)

        # 创建菜单栏
        self.create_menu()

        # 状态栏
        self.statusBar().showMessage("就绪")

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction("退出", self.close, "Ctrl+Q")

        window_menu = menubar.addMenu("窗口(&W)")
        window_menu.addAction("关于", self.show_about)

    def show_message_box(self):
        # 演示QMessageBox
        reply = QMessageBox.question(
            self, '确认',
            "你确定要执行此操作吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.statusBar().showMessage("用户选择了：是")
        else:
            self.statusBar().showMessage("用户选择了：否")

    def show_file_dialog(self):
        # 演示QFileDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "所有文件 (*.*);;文本文件 (*.txt)"
        )

        if file_name:
            self.statusBar().showMessage(f"选择的文件: {file_name}")

    def show_input_dialog(self):
        # 演示QInputDialog
        text, ok = QInputDialog.getText(self, "输入", "请输入你的名字:")

        if ok and text:
            self.statusBar().showMessage(f"输入的名字: {text}")

    def show_color_dialog(self):
        # 演示QColorDialog
        color = QColorDialog.getColor(Qt.white, self, "选择颜色")

        if color.isValid():
            # 更改按钮颜色
            self.sender().setStyleSheet(f"background-color: {color.name()}")
            self.statusBar().showMessage(f"选择的颜色: {color.name()}")

    def show_font_dialog(self):
        # 演示QFontDialog
        font, ok = QFontDialog.getFont(self)

        if ok:
            self.sender().setFont(font)
            self.statusBar().showMessage(f"选择的字体: {font.family()}")

    def show_progress_dialog(self):
        # 演示QProgressDialog
        progress = QProgressDialog("处理中...", "取消", 0, 100, self)
        progress.setWindowTitle("进度")
        progress.setWindowModality(Qt.WindowModal)

        # 模拟进度更新
        progress.show()
        for i in range(101):
            progress.setValue(i)
            QApplication.processEvents()  # 处理事件，保持UI响应
            if progress.wasCanceled():
                break
            QThread.msleep(20)  # 延迟20ms模拟处理时间

        progress.close()
        self.statusBar().showMessage("进度完成")

    def show_wizard(self):
        # 演示QWizard
        wizard = QWizard(self)
        wizard.setWindowTitle("设置向导")

        # 添加页面
        page1 = QWizardPage()
        page1.setTitle("第一步")
        page1.setSubTitle("基本信息设置")

        page2 = QWizardPage()
        page2.setTitle("第二步")
        page2.setSubTitle("高级设置")

        page3 = QWizardPage()
        page3.setTitle("完成")
        page3.setSubTitle("设置完成")

        wizard.addPage(page1)
        wizard.addPage(page2)
        wizard.addPage(page3)

        wizard.exec_()
        self.statusBar().showMessage("向导完成")

    def open_standalone_window(self):
        # 演示QWidget作为独立窗口
        window = QWidget()
        window.setWindowTitle("独立窗口")
        window.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("这是一个独立的QWidget窗口"))
        layout.addWidget(QPushButton("关闭", clicked=window.close))

        window.setLayout(layout)
        window.show()

    def show_custom_dialog(self):
        # 演示自定义QDialog
        dialog = CustomDialog(self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            self.statusBar().showMessage(f"用户输入: {dialog.get_data()}")

    def show_about(self):
        # 使用QMessageBox显示关于信息
        QMessageBox.about(self, "关于",
                          "PyQt5窗口类演示程序\n\n"
                          "展示了PyQt5中各种窗口类的使用方法。"
                          )


class CustomDialog(QDialog):
    """自定义对话框示例"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义对话框")
        self.setModal(True)

        layout = QVBoxLayout()

        # 表单布局
        form_layout = QFormLayout()
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.age_spin = QSpinBox()
        self.age_spin.setRange(1, 120)

        form_layout.addRow("姓名:", self.name_edit)
        form_layout.addRow("邮箱:", self.email_edit)
        form_layout.addRow("年龄:", self.age_spin)

        layout.addLayout(form_layout)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        """获取用户输入的数据"""
        return {
            "name": self.name_edit.text(),
            "email": self.email_edit.text(),
            "age": self.age_spin.value()
        }


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainApplication()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
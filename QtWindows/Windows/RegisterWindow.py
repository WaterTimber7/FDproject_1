import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDialog
from PyQt5.QtCore import Qt
from QtWindows.SQlite.DataValidator import DataValidator
from QtWindows.SQlite.DataManager import SQLiteManager

from PyQt5.QtWidgets import QLineEdit


class SmartLineEdit(QLineEdit):
    """
    安全的输入框：
    - 统一处理 focusInEvent
    - 支持传入回调
    - 不破坏 Qt C++ 虚函数
    """

    def __init__(self, parent=None, on_focus_callback=None):
        super().__init__(parent)
        self.on_focus_callback = on_focus_callback

    def focusInEvent(self, event):
        # 1️⃣ 先做我们自己的逻辑
        if callable(self.on_focus_callback):
            self.on_focus_callback(self)

        # 2️⃣ 一定要调用父类（非常重要）
        super().focusInEvent(event)


class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("注册界面打开成功")
        self.setWindowTitle("注册界面")  # 设置窗口标题
        self.setGeometry(400, 400, 600, 800)  # 设置窗口位置和大小
        self.database = SQLiteManager('./QtWindows/SQlite/users.db')

        # 创建垂直布局
        layout = QVBoxLayout()

        # 创建标题标签
        title_label = QLabel('注册')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 24px; font-weight: bold;')
        layout.addWidget(title_label)

        # 创建姓名输入框
        self.name_input = SmartLineEdit(self, self.on_input_focus)
        self.name_input.setPlaceholderText("请输入姓名")
        self.name_input.setStyleSheet('padding: 10px; font-size: 14px;')
        layout.addWidget(self.name_input)

        self.name_error_label = QLabel('')
        self.name_error_label.setStyleSheet('color: red; font-size: 14px;')
        layout.addWidget(self.name_error_label)

        # 创建电话输入框
        self.phone_input = SmartLineEdit(self, self.on_input_focus)
        self.phone_input.setPlaceholderText("请输入电话")
        self.phone_input.setStyleSheet('padding: 10px; font-size: 14px;')
        layout.addWidget(self.phone_input)

        self.phone_error_label = QLabel('')
        self.phone_error_label.setStyleSheet('color: red; font-size: 14px;')
        layout.addWidget(self.phone_error_label)

        # 创建邮箱输入框
        self.email_input = SmartLineEdit(self, self.on_input_focus)
        self.email_input.setPlaceholderText("请输入邮箱")
        self.email_input.setStyleSheet('padding: 10px; font-size: 14px;')
        layout.addWidget(self.email_input)

        self.email_error_label = QLabel('')
        self.email_error_label.setStyleSheet('color: red; font-size: 14px;')
        layout.addWidget(self.email_error_label)

        # 创建密码输入框
        self.password_input = SmartLineEdit(self, self.on_input_focus)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.password_input.setStyleSheet('padding: 10px; font-size: 14px;')
        layout.addWidget(self.password_input)

        self.password_error_label = QLabel('')
        self.password_error_label.setStyleSheet('color: red; font-size: 14px;')
        layout.addWidget(self.password_error_label)

        # 创建确认密码输入框
        self.confirm_password_input = SmartLineEdit(self, self.on_input_focus)
        self.confirm_password_input.setPlaceholderText("确认密码")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet('padding: 10px; font-size: 14px;')
        layout.addWidget(self.confirm_password_input)

        self.confirm_password_error_label = QLabel('')
        self.confirm_password_error_label.setStyleSheet('color: red; font-size: 14px;')
        layout.addWidget(self.confirm_password_error_label)

        # self.name_input.focusInEvent = self.clear_error_messages
        # self.email_input.focusInEvent = self.clear_error_messages
        # self.phone_input.focusInEvent = self.clear_error_messages
        # self.password_input.focusInEvent = self.clear_error_messages
        # self.confirm_password_input.focusInEvent = self.clear_error_messages

        # 创建注册按钮
        register_button = QPushButton("注册")
        register_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 16px;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388e3c;
                transform: translateY(2px);
            }
        """)
        layout.addWidget(register_button)

        # 创建注册提示小字，点击可以跳转或处理事件
        register_tip_button = QPushButton("已有账号？点击登录")
        register_tip_button.setStyleSheet('font-size: 14px; color: #007BFF; background: none; border: none; text-decoration: underline;')
        register_tip_button.clicked.connect(self.close)
        layout.addWidget(register_tip_button)

        # 添加一个弹性空间，把所有控件推到顶部
        layout.addStretch(1)

        # 创建退出按钮
        quit_button = QPushButton("退出")
        quit_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                background-color: #f44336;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
            }
        """)
        quit_button.clicked.connect(self.close)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(quit_button)
        layout.addLayout(bottom_layout)

        # 设置主布局
        self.setLayout(layout)

        # 连接注册按钮点击事件
        register_button.clicked.connect(self.on_register_clicked)

    def on_register_clicked(self):

        # 获取输入内容
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if password != confirm_password:
            self.confirm_password_error_label.setText("两次密码不一致！")
            self.confirm_password_input.setStyleSheet("border: 2px solid red;")
            return

        # 验证数据
        user_data = {
            'name': name,
            'phone': phone,
            'email': email,
            'password': password,
        }

        result = DataValidator.validate_fields(user_data)
        print(result)

        # 检查验证结果
        if not result.get('name') == True:
            self.name_error_label.setText(result.get('name'))
            self.name_input.setStyleSheet("border: 2px solid red;")

        if not result.get('phone') == True:
            self.phone_error_label.setText(result.get('phone'))
            self.phone_input.setStyleSheet("border: 2px solid red;")

        if not result.get('email') == True:
            self.email_error_label.setText(result.get('email'))
            self.email_input.setStyleSheet("border: 2px solid red;")

        if not result.get('password') == True:
            self.password_error_label.setText(result.get('password'))
            self.password_input.setStyleSheet("border: 2px solid red;")

        # 如果有任何错误，返回
        if (result.get('name') != True or result.get('phone') != True or result.get('email') != True or result.get(
                'password') != True):
            return

        self.show_message()
        print('验证通过')
        # 如果所有验证通过，进行注册
        #hashed_password = SQLiteManager.hashlib_password(password)
        self.database.add_user(name=name,phone=phone,email=email,password=password,permission_level=0)
        #print(f"name: {name}, phone: {phone}, email: {email}, input_password: {password}, hashed_password: {hashed_password}")
        self.close()

    def clear_error_messages(self, event):
        # 清除错误信息和红色边框
        self.name_error_label.clear()
        self.phone_error_label.clear()
        self.email_error_label.clear()
        self.password_error_label.clear()
        self.confirm_password_error_label.clear()

        # 恢复输入框样式
        self.name_input.setStyleSheet('padding: 10px; font-size: 14px;')
        self.phone_input.setStyleSheet('padding: 10px; font-size: 14px;')
        self.email_input.setStyleSheet('padding: 10px; font-size: 14px;')
        self.password_input.setStyleSheet('padding: 10px; font-size: 14px;')
        self.confirm_password_input.setStyleSheet('padding: 10px; font-size: 14px;')
        event.accept()

    def show_message(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("注册成功")  # 设置消息框标题
        msg_box.setText("恭喜！您的账户注册成功！")  # 设置消息框的文本
        msg_box.setStandardButtons(QMessageBox.Ok)  # 设置消息框的按钮
        msg_box.exec_()

    def on_input_focus(self, input_widget):
        """
        任意输入框获得焦点时触发
        """
        # 清除所有错误提示
        self.name_error_label.clear()
        self.phone_error_label.clear()
        self.email_error_label.clear()
        self.password_error_label.clear()
        self.confirm_password_error_label.clear()

        # 恢复所有输入框样式
        for widget in [
            self.name_input,
            self.phone_input,
            self.email_input,
            self.password_input,
            self.confirm_password_input
        ]:
            widget.setStyleSheet('padding: 10px; font-size: 14px;')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    register_window = RegisterWindow()
    register_window.show()
    sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from QtWindows.SQlite.DataManager import SQLiteManager
from QtWindows.Windows.RegisterWindow import RegisterWindow
from QtWindows.Windows.AdminMainWindow import AdminMainWindow

class AdminLoginWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.database = SQLiteManager('./QtWindows/SQlite/users.db')

        self.setWindowTitle("管理员登录界面")
        self.setGeometry(400, 400, 600, 800)
        self.is_login = False

        layout = QVBoxLayout()

        title_label = QLabel('管理员登录')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 24px; font-weight: bold;')
        layout.addWidget(title_label)

        layout.addStretch(1)
        self.setLayout(layout)

        self.userphone_input = QLineEdit(self)
        self.userphone_input.setPlaceholderText("请输入管理员uid")
        self.userphone_input.setStyleSheet('padding: 10px; font-size: 14px;')
        layout.addWidget(self.userphone_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet('padding: 10px; font-size: 14px;')
        layout.addWidget(self.password_input)

        login_button = QPushButton("登录")
        login_button.setStyleSheet("""
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
        layout.addWidget(login_button)

        register_button = QPushButton("注册")
        register_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 12px;
                color: #007BFF;
                background: none;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #0056b3;
            }
        """)
        layout.addWidget(register_button)
        register_button.clicked.connect(self.on_register_clicked)

        layout.addStretch(1)
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
        self.setLayout(layout)

        login_button.clicked.connect(self.on_login_clicked)

    def on_login_clicked(self):
        input_phone = self.userphone_input.text()
        input_password = self.password_input.text()

        user_info = self.database.get_user(input_phone)
        user_phone = -1
        user_password = -1
        permission_level = 0

        if user_info:
            user_phone = user_info['phone']
            user_password = user_info['password']
            permission_level = user_info.get('permission_level', 0)

        if (input_phone == user_phone) and (user_password == SQLiteManager.hashlib_password(input_password)):
            if permission_level == 5:
                print("管理员登录成功！")
                self.is_login = True
                
                # 创建管理员主窗口并传递权限级别
                self.window = AdminMainWindow(permission_level=permission_level)
                self.window.show()
                self.close()
            else:
                self.show_admin_only_message()
                self.userphone_input.clear()
                self.password_input.clear()
        else:
            self.show_error_message()
            self.userphone_input.clear()
            self.password_input.clear()

    def show_error_message(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("登录失败")
        msg_box.setText("账号或密码错误")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_admin_only_message(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("权限不足")
        msg_box.setText("仅限管理员登录（permission_level=5）。")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def on_register_clicked(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = AdminLoginWindow()
    login_window.show()
    sys.exit(app.exec_())

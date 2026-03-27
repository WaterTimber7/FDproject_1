import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from QtWindows.SQlite.DataManager import SQLiteManager
from QtWindows.Windows.RegisterWindow import RegisterWindow
from QtWindows.Windows.MainWindo import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.database = SQLiteManager('./QtWindows/SQlite/users.db')

        self.setWindowTitle("登录界面")
        self.setGeometry(400, 400, 600, 800)
        self.setStyleSheet("background-color: #F5F7FA;")
        self.is_login = False

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        title_label = QLabel('登录')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #303133;")
        layout.addWidget(title_label)

        layout.addStretch(1)
        self.setLayout(layout)

        self.userphone_input = QLineEdit(self)
        self.userphone_input.setPlaceholderText("请输入uid")
        layout.addWidget(self.userphone_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("登 录")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #409EFF;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #66B1FF;
            }
            QPushButton:pressed {
                background-color: #3A8EE6;
                padding-top: 12px;
                padding-bottom: 8px;
            }
        """)
        layout.addWidget(login_button)

        register_button = QPushButton("还没有账号？立即注册")
        register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #409EFF;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #66B1FF;
            }
        """)
        layout.addWidget(register_button)

        register_button.clicked.connect(self.on_register_clicked)

        layout.addStretch(1)

        quit_button = QPushButton("退 出")
        quit_button.setStyleSheet("""
            QPushButton {
                background-color: #F56C6C;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F89898;
            }
            QPushButton:pressed {
                background-color: #E6A23C;
            }
        """)
        layout.addWidget(quit_button)
        quit_button.clicked.connect(self.close)

        # 创建水平布局来放置退出按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)  # 将退出按钮推到右边
        bottom_layout.addWidget(quit_button)  # 将退出按钮添加到布局中

        # 将水平布局添加到垂直布局的底部
        layout.addLayout(bottom_layout)
        self.setLayout(layout)
        login_button.clicked.connect(self.on_login_clicked)

    def on_login_clicked(self):
        print(111111)
        input_phone = self.userphone_input.text()
        input_password = self.password_input.text()

        user_info = self.database.get_user(input_phone)
        self.database.get_all_users()
        print("登录信息：\n")
        print(user_info)
        user_phone = -1
        user_password = -1

        if  user_info:
            print("查询成功")
            user_phone = user_info['phone']
            user_password = user_info['password']

        print(f"user_phone: {user_phone}, user_password: {user_password}, \ninput_phone: {input_phone}, input_hashlib_password: {SQLiteManager.hashlib_password(input_password)}, input_password: {input_password}")
        # 检查账号和密码是否正确
        if (input_phone == user_phone) and (user_password == SQLiteManager.hashlib_password(input_password)):
            # 获取用户权限级别
            permission_level = user_info.get('permission_level', 0) if user_info else 0
            print(f"用户权限级别: {permission_level}")
            
            # 检查是否为权限5（超级管理员），如果是则不允许登录
            if permission_level == 5:
                print("权限5用户请使用管理员登录界面")
                self.show_admin_only_message()
                self.userphone_input.clear()
                self.password_input.clear()
                return
            
            print("登录成功！")
            self.is_login = True
            
            # 创建主窗口并传递权限级别
            self.window = MainWindow(permission_level=permission_level)
            self.window.show()
            self.close()
        else:
            # 弹出错误提示框
            self.show_error_message()
            # 清空账号和密码框内容
            self.userphone_input.clear()
            self.password_input.clear()

    def show_error_message(self):
        # 创建一个消息框并设置其标题、信息和按钮
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)  # 设置消息框的图标为错误图标
        msg_box.setWindowTitle("登录失败")  # 设置消息框标题
        msg_box.setText("账号或密码错误")  # 设置消息框的文本
        msg_box.setStandardButtons(QMessageBox.Ok)  # 设置消息框的按钮
        msg_box.exec_()

    def show_admin_only_message(self):
        """显示仅限管理员登录的提示信息"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("权限限制")
        msg_box.setText("权限5用户请使用管理员登录界面登录。")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def on_register_clicked(self):
        # 点击注册链接时关闭登录窗口并打开注册窗口
        print("打开注册界面")
        #self.close()  # 关闭当前登录窗口
        self.register_window = RegisterWindow()  # 打开注册窗口
        self.register_window.show()
        self.database.add_user(name=name,phone=phone,email=email,password=password,permission_level=0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
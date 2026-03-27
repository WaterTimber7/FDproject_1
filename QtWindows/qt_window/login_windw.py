
from QtWindows.qt_window import QuadWindow
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class LoginWindow(QWidget):
    def __init__(self):
        # 调用父类QWidget的初始化方法
        super().__init__()

        # 初始化用户界面
        self.init_ui()

    # 初始化用户界面的方法
    def init_ui(self):
        # 设置窗口标题为'登录'
        self.setWindowTitle('AAAA登录')

        # 设置窗口尺寸为宽度400像素，高度700像素
        # 参数说明：setFixedSize(width, height)
        # width: 窗口宽度
        # height: 窗口高度
        # 使用setFixedSize固定窗口大小，用户不能调整窗口尺寸
        self.setFixedSize(400, 700)

        # 创建主布局管理器
        # QVBoxLayout: 垂直布局，从上到下排列子控件
        main_layout = QVBoxLayout()

        # 设置布局的边距（左、上、右、下）
        # 参数说明：setContentsMargins(left, top, right, bottom)
        # 这里设置为50像素的边距，使内容与窗口边缘保持距离
        main_layout.setContentsMargins(50, 50, 50, 50)

        # 设置布局内控件之间的间距
        # 参数说明：setSpacing(spacing)
        # 这里设置为30像素，使控件之间有足够的间隔
        main_layout.setSpacing(30)

        # 创建应用标题标签
        # QLabel: 标签控件，用于显示文本
        title_label = QLabel('BBBBB')

        # 设置标题字体
        # QFont: 字体对象
        # 参数说明：QFont(family, size, weight)
        # family: 字体族，这里使用'Arial'
        # size: 字体大小，这里设置为24点
        # weight: 字体粗细，QFont.Bold表示粗体
        title_label.setFont(QFont('Arial', 24, QFont.Bold))

        # 设置标签文本的颜色
        # 使用HTML样式设置文本颜色为深蓝色
        title_label.setStyleSheet('color: blue;')

        # 设置标签的对齐方式为居中对齐
        # Qt.AlignCenter: 水平和垂直都居中对齐
        title_label.setAlignment(Qt.AlignCenter)

        # 将标题标签添加到主布局中
        main_layout.addWidget(title_label)

        # 在标题下方添加弹性空间
        # addStretch: 添加一个可拉伸的空间
        # 参数1: 拉伸因子，表示相对于其他拉伸空间的占比
        # 这里添加一个可拉伸的空间，使标题与表单之间有间隔
        main_layout.addStretch(1)

        # 创建账号输入区域
        # 账号区域使用垂直布局
        username_layout = QVBoxLayout()

        # 创建账号标签
        username_label = QLabel('账号:')

        # 设置账号标签的字体
        username_label.setFont(QFont('Microsoft YaHei', 12))

        # 设置账号标签的文本颜色
        username_label.setStyleSheet('color: green;')

        # 将账号标签添加到账号布局中
        username_layout.addWidget(username_label)

        # 创建账号输入框
        # QLineEdit: 单行文本输入框
        self.username_input = QLineEdit()

        # 设置账号输入框的占位符文本
        # 占位符文本：当输入框为空时显示的提示文本
        self.username_input.setPlaceholderText('请输入账号')

        # 设置账号输入框的最小高度
        self.username_input.setMinimumHeight(45)

        # 设置账号输入框的样式
        # 使用CSS样式字符串美化输入框
        # padding: 内边距，使文本与边框之间有距离
        # border: 边框样式，1像素宽的实线边框
        # border-radius: 边框圆角半径，5像素
        # font-size: 字体大小，14像素
        self.username_input.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                border: 1px solid #bac3m7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        ''')

        # 将账号输入框添加到账号布局中
        username_layout.addWidget(self.username_input)

        # 将账号布局添加到主布局中
        main_layout.addLayout(username_layout)

        # 创建密码输入区域
        # 密码区域使用垂直布局
        password_layout = QVBoxLayout()

        # 创建密码标签
        password_label = QLabel('密码:')

        # 设置密码标签的字体
        password_label.setFont(QFont('Microsoft YaHei', 12))

        # 设置密码标签的文本颜色
        password_label.setStyleSheet('color: #34495e;')

        # 将密码标签添加到密码布局中
        password_layout.addWidget(password_label)

        # 创建密码输入框
        self.password_input = QLineEdit()

        # 设置密码输入框的占位符文本
        self.password_input.setPlaceholderText('请输入密码')

        # 设置密码输入框的最小高度
        self.password_input.setMinimumHeight(45)

        # 设置密码输入框的回显模式为密码模式
        # QLineEdit.Password: 密码模式，输入的字符显示为圆点(•)
        self.password_input.setEchoMode(QLineEdit.Password)

        # 设置密码输入框的样式
        self.password_input.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        ''')

        # 将密码输入框添加到密码布局中
        password_layout.addWidget(self.password_input)

        # 将密码布局添加到主布局中
        main_layout.addLayout(password_layout)

        # 在密码区域和登录按钮之间添加弹性空间
        main_layout.addStretch(2)

        # 创建登录按钮
        # QPushButton: 按钮控件
        login_button = QPushButton('登录')

        # 设置登录按钮的最小高度
        login_button.setMinimumHeight(50)

        # 设置登录按钮的字体
        login_button.setFont(QFont('Microsoft YaHei', 14, QFont.Bold))

        # 设置登录按钮的样式
        # 使用CSS样式字符串美化按钮
        # background-color: 背景颜色
        # color: 文本颜色
        # border: 边框样式，无边框
        # border-radius: 边框圆角半径
        # :hover: 鼠标悬停时的样式
        # :pressed: 鼠标按下时的样式
        login_button.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        ''')

        # 将登录按钮连接到登录处理方法
        # clicked: 按钮的点击信号
        # connect: 连接信号到槽函数
        # self.handle_login: 槽函数，处理登录逻辑
        login_button.clicked.connect(self.handle_login)

        # 将登录按钮添加到主布局中
        main_layout.addWidget(login_button)

        # 将主布局设置为窗口的布局
        self.setLayout(main_layout)

        # 设置窗口的背景颜色
        # 使用setStyleSheet设置窗口的背景色
        # background-color: 背景颜色
        self.setStyleSheet('background-color: #ecf0f1;')

    # 处理登录的方法
    def handle_login(self):
        # 获取账号输入框的文本内容
        # text(): 获取文本框中的文本
        # strip(): 去除文本两端的空白字符
        username = self.username_input.text().strip()

        # 获取密码输入框的文本内容
        password = self.password_input.text().strip()

        # 检查账号和密码是否为空
        if not username:
            # 如果账号为空，设置输入框焦点并添加提示样式
            self.username_input.setFocus()
            self.username_input.setStyleSheet('''
                QLineEdit {
                    padding: 10px;
                    border: 1px solid #e74c3c;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #3498db;
                }
            ''')
            return  # 终止方法执行

        if not password:
            # 如果密码为空，设置输入框焦点并添加提示样式
            self.password_input.setFocus()
            self.password_input.setStyleSheet('''
                QLineEdit {
                    padding: 10px;
                    border: 1px solid #e74c3c;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #3498db;
                }
            ''')
            return  # 终止方法执行

        # 如果账号和密码都不为空，打印登录信息
        # 在实际应用中，这里应该进行用户验证
        print(f'账号: {username}')
        print(f'密码: {password}')
        print('正在验证登录信息...')

        # 恢复输入框的正常样式
        self.username_input.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        ''')

        self.password_input.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        ''')

        # 模拟登录验证（这里只是示例）
        # 在实际应用中，这里应该连接数据库或API进行验证
        if username == 'a' and password == '1':
            QMessageBox.information(self, "登录成功", "登录成功！正在跳转到主界面...")

            # 创建主窗口实例
            self.quad_window = QuadWindow("四分区窗口演示程序")
            self.quad_window.resize(1400, 1400)
            # 显示主窗口
            self.quad_window.show()
            self.username_input.clear()  # 清空账号输入框
            self.password_input.clear()  # 清空密码输入框

            self.close()
        else:
            QMessageBox.critical(self, "登录失败", "账号或密码错误！\n\n请检查您的账号和密码，然后重试。")

            # 密码输入错误后清空密码框并设置焦点
            self.password_input.clear()
            self.password_input.setFocus()


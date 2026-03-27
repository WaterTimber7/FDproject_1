from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QHeaderView, QFormLayout,
    QGroupBox
)
from PyQt5.QtCore import Qt
from QtWindows.SQlite.DataManager import SQLiteManager
from QtWindows.SQlite.DataValidator import DataValidator
import os

class UserManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        # 使用绝对路径连接数据库
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, '../SQlite/users.db')
        self.database = SQLiteManager(db_path)
        self._setup_ui()
        self.load_users()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 1. 顶部：标题和刷新
        top_layout = QHBoxLayout()
        title = QLabel("用户管理 (非管理员)")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        refresh_btn = QPushButton("刷新列表")
        refresh_btn.clicked.connect(self.load_users)
        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(refresh_btn)
        layout.addLayout(top_layout)

        # 2. 中部：用户列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "姓名", "电话", "邮箱", "权限"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # 不可直接在表格编辑
        self.table.itemClicked.connect(self.on_table_item_clicked)
        layout.addWidget(self.table)

        # 3. 底部：操作区域
        operation_group = QGroupBox("用户信息操作")
        op_layout = QHBoxLayout(operation_group)

        # 左侧表单
        form_layout = QFormLayout()
        self.input_name = QLineEdit()
        self.input_phone = QLineEdit()
        self.input_email = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("修改/添加时填写，留空不改")
        
        # 权限只能是 0, 1, 2 等，不能是 5
        self.input_permission = QLineEdit()
        self.input_permission.setPlaceholderText("0=普通, 1=VIP等 (不能为5)")

        form_layout.addRow("姓名:", self.input_name)
        form_layout.addRow("电话:", self.input_phone)
        form_layout.addRow("邮箱:", self.input_email)
        form_layout.addRow("密码:", self.input_password)
        form_layout.addRow("权限:", self.input_permission)
        
        op_layout.addLayout(form_layout, stretch=2)

        # 右侧按钮
        btn_layout = QVBoxLayout()
        self.btn_add = QPushButton("添加用户")
        self.btn_update = QPushButton("更新用户")
        self.btn_delete = QPushButton("删除用户")
        self.btn_clear = QPushButton("清空输入")

        self.btn_add.clicked.connect(self.add_user)
        self.btn_update.clicked.connect(self.update_user)
        self.btn_delete.clicked.connect(self.delete_user)
        self.btn_clear.clicked.connect(self.clear_inputs)
        
        # 样式美化
        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_clear]:
            btn.setMinimumHeight(30)
        
        self.btn_add.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_update.setStyleSheet("background-color: #2196F3; color: white;")
        self.btn_delete.setStyleSheet("background-color: #f44336; color: white;")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        
        op_layout.addLayout(btn_layout, stretch=1)
        
        layout.addWidget(operation_group)

    def load_users(self):
        """加载非管理员用户到表格"""
        self.table.setRowCount(0)
        # SQLiteManager 没有直接返回所有用户的列表的方法(get_all_users是直接print)，我们需要修改或添加一个方法
        # 暂时只能用 execute 直接查询，因为 DataManager.get_all_users 只是打印
        # 更好的是去给 SQLiteManager 加一个 fetch_all_users 方法，但为了不改动太多核心库，我直接用 cursor
        # 必须确保 cursor 是可用的。SQLiteManager 继承自 SQLiteDB，有 self.cursor
        
        try:
            self.database.cursor.execute("SELECT * FROM users WHERE permission_level != 5")
            users = self.database.cursor.fetchall()
            
            self.table.setRowCount(len(users))
            for row_idx, user in enumerate(users):
                # user: (id, name, phone, email, password, permission_level)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(user[0])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(user[1]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(user[2]))
                self.table.setItem(row_idx, 3, QTableWidgetItem(user[3]))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(user[5])))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载用户失败: {e}")

    def on_table_item_clicked(self, item):
        row = item.row()
        self.input_name.setText(self.table.item(row, 1).text())
        self.input_phone.setText(self.table.item(row, 2).text())
        self.input_email.setText(self.table.item(row, 3).text())
        self.input_permission.setText(self.table.item(row, 4).text())
        self.input_password.clear() # 密码不回显
        
        # 记录当前选中的 phone，用于更新和删除
        self.current_phone = self.table.item(row, 2).text()

    def clear_inputs(self):
        self.input_name.clear()
        self.input_phone.clear()
        self.input_email.clear()
        self.input_password.clear()
        self.input_permission.clear()
        if hasattr(self, 'current_phone'):
            del self.current_phone

    def add_user(self):
        name = self.input_name.text()
        phone = self.input_phone.text()
        email = self.input_email.text()
        password = self.input_password.text()
        perm_str = self.input_permission.text()

        # 校验
        if not all([name, phone, email, password, perm_str]):
            QMessageBox.warning(self, "提示", "请填写所有字段")
            return
            
        try:
            perm = int(perm_str)
            if perm == 5:
                QMessageBox.warning(self, "禁止", "不能添加管理员账户")
                return
        except ValueError:
            QMessageBox.warning(self, "错误", "权限必须是整数")
            return

        # 验证器
        val_res = DataValidator.validate_fields({
            'name': name, 'phone': phone, 'email': email, 'password': password
        })
        for k, v in val_res.items():
            if v is not True:
                QMessageBox.warning(self, "验证失败", f"{k}: {v}")
                return

        # 添加
        # SQLiteManager.add_user 内部有 print，没有返回值判断成功与否，需要我们自己捕获异常或修改
        # 这里直接调用，然后刷新列表看结果
        # 注意：SQLiteManager.add_user 的 permission_level 参数
        
        # 为了捕获错误，最好是在这里先检查一下是否存在
        self.database.add_user(name, phone, email, password, perm)
        # 简单处理：重新加载列表，如果有了就是成功
        self.load_users()
        self.clear_inputs()
        QMessageBox.information(self, "操作", "尝试添加用户完成，请检查列表")

    def update_user(self):
        if not hasattr(self, 'current_phone') or not self.current_phone:
            QMessageBox.warning(self, "提示", "请先从列表中选择一个用户")
            return

        name = self.input_name.text()
        email = self.input_email.text()
        password = self.input_password.text()
        perm_str = self.input_permission.text()
        
        perm = None
        if perm_str:
            try:
                perm = int(perm_str)
                if perm == 5:
                    QMessageBox.warning(self, "禁止", "不能设置为管理员权限")
                    return
            except ValueError:
                QMessageBox.warning(self, "错误", "权限必须是整数")
                return

        # 这里的 phone 是新的 phone 还是旧的？
        # update_user(self, phone, name=None, email=None, password=None, permission_level=None)
        # 这里的 phone 是指 WHERE phone = ?，所以应该是 self.current_phone
        # 如果用户修改了输入框里的 phone，目前的 DataManager.update_user 不支持修改 phone 本身
        # 如果用户想改 phone，需要删了重加，或者修改 DataManager
        # 这里假设不能修改 phone，或者提示用户 phone 不可改
        
        new_phone = self.input_phone.text()
        if new_phone != self.current_phone:
            QMessageBox.information(self, "提示", "暂不支持直接修改手机号(ID)，请删除后重新添加")
            self.input_phone.setText(self.current_phone)
            return

        self.database.update_user(
            self.current_phone, 
            name if name else None, 
            email if email else None, 
            password if password else None, 
            perm
        )
        self.load_users()
        QMessageBox.information(self, "操作", "更新完成")

    def delete_user(self):
        if not hasattr(self, 'current_phone') or not self.current_phone:
            QMessageBox.warning(self, "提示", "请先从列表中选择一个用户")
            return

        reply = QMessageBox.question(self, '确认', f"确定要删除用户 {self.current_phone} 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.database.delete_user(self.current_phone)
            self.load_users()
            self.clear_inputs()
            QMessageBox.information(self, "操作", "删除完成")
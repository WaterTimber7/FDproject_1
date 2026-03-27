import sqlite3
import hashlib
from QtWindows.SQlite.CreateData import SQLiteDB

class SQLiteManager(SQLiteDB):
    def __init__(self, db_name):
        super().__init__(db_name)

    def add_user(self, name, phone, email, password, permission_level):
        """通过 phone 添加用户，并确保 phone、email 都是唯一的"""
        try:
            # 检查 phone 是否已经存在
            self.cursor.execute('''SELECT * FROM users WHERE phone = ?''', (phone,))
            existing_user = self.cursor.fetchone()
            if existing_user:
                print(f"手机号 {phone} 已存在，添加失败！")
                return

            # 检查 email 是否已经存在
            self.cursor.execute('''SELECT * FROM users WHERE email = ?''', (email,))
            existing_user = self.cursor.fetchone()
            if existing_user:
                print(f"邮箱 {email} 已存在，添加失败！")
                return

            # 如果没有重复，插入新用户
            self.cursor.execute('''
                INSERT INTO users (name, phone, email, password, permission_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, phone, email, SQLiteManager.hashlib_password(password), permission_level))
            self.connection.commit()
            print(f"用户 {name} 添加成功！")
        except sqlite3.IntegrityError:
            print(f"添加失败！数据库错误。")

    @staticmethod
    def hashlib_password(password):
        """哈希加密密码"""
        return hashlib.sha256(password.encode()).hexdigest()

    def delete_user(self, phone):
        """根据 phone 删除用户"""
        self.cursor.execute('''DELETE FROM users WHERE phone = ?''', (phone,))
        self.connection.commit()
        print(f"手机号 {phone} 的用户已被删除。")

    def update_user(self, phone, name=None, email=None, password=None, permission_level=None):
        """根据 phone 更新用户信息"""
        updates = []
        params = []

        if name:
            updates.append("name = ?")
            params.append(name)
        if email:
            updates.append("email = ?")
            params.append(email)
        if password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            updates.append("password = ?")
            params.append(hashed_password)
        if permission_level is not None:
            updates.append("permission_level = ?")
            params.append(permission_level)

        # 防止没有更新任何字段
        if not updates:
            print("没有需要更新的信息！")
            return

        updates_str = ", ".join(updates)
        params.append(phone)

        self.cursor.execute(f'''
        UPDATE users
        SET {updates_str}
        WHERE phone = ?
        ''', params)
        self.connection.commit()
        print(f"手机号 {phone} 的用户信息已更新。")

    def get_user(self, phone):
        """根据 phone 查询用户信息"""
        self.cursor.execute('''SELECT * FROM users WHERE phone = ?''', (phone,))
        user = self.cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'name': user[1],
                'phone': user[2],
                'email': user[3],
                'password': user[4],  # 不返回密码明文
                'permission_level': user[5]
            }
        else:
            print(f"手机号 {phone} 的用户不存在！")
            return 0

    def get_all_users(self):
        """输出表中的所有内容"""
        self.cursor.execute('''SELECT * FROM users''')
        users = self.cursor.fetchall()  # 获取所有用户记录
        if users:
            print("所有用户信息：")
            for user in users:
                print({
                    'id': user[0],
                    'name': user[1],
                    'phone': user[2],
                    'email': user[3],
                    'password': user[4],  # 不返回密码明文
                    'permission_level': user[5]
                })
        else:
            print("没有用户数据。")

    def close(self):
        """关闭数据库连接"""
        self.connection.close()

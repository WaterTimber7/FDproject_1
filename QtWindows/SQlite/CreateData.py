import sqlite3

class SQLiteDB:
    def __init__(self, db_name):
        # 数据库文件名
        self.db_name = db_name
        # 连接到数据库
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_table(self):
        # 创建用户表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            permission_level INTEGER NOT NULL
        )
        ''')
        # 提交更改
        self.connection.commit()

    def close(self):
        # 关闭数据库连接
        self.connection.close()

# 使用示例
db = SQLiteDB('users.db')
db.create_table()  # 创建表
db.close()  # 关闭连接

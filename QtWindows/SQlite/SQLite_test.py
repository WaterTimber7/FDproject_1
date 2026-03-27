
from DataManager import SQLiteManager
from DataValidator import DataValidator


if __name__ == '__main__':


    db_operations = SQLiteManager('users.db')

    print(22222222)
    # db_operations.delete_user(11111111111)
    #db_operations.delete_user(00000000000)

    # db_operations.add_user(name='aaa',phone='17879889000',email="128746@116.com",password="123456",permission_level=5)
    db_operations.add_user(name='权限five',phone='55555555556',email="935526@555.com",password="12345678m",permission_level=5)
    # db_operations.add_user(name='权限tow',phone='22222222222', email="1233326@116.com", password="12345678m",permission_level=2)

    db_operations.get_all_users()
    print(db_operations)

    db_operations.close()
    # 查询用户
   # user_info = db_operations.get_user("44445678")
   # print(user_info)
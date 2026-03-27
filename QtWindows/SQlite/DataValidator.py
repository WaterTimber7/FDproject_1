import re

class DataValidator:
    @staticmethod
    def validate_name(name):
        """检查姓名是否合法：只允许中英文字符"""
        if not name:
            return "姓名不能为空"
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z]+$', name):
            return "姓名只能包含中英文字符"
        return True

    @staticmethod
    def validate_email(email):
        """检查邮箱格式是否合法"""
        if not email or not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            return "无效的邮箱格式"
        return True

    @staticmethod
    def validate_password(password):
        """检查密码的复杂度：至少8个字符，包含字母和数字"""
        if len(password) < 8:
            return "密码长度必须至少为8个字符"
        if not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password):
            return "密码必须包含字母和数字"
        return True

    @staticmethod
    def validate_phone(phone):
        """检查电话是否合法：11位数字"""
        if not re.match(r'^\d{11}$', phone):
            return "无效的电话号码，必须是11位数字"
        return True

    @staticmethod
    def validate_permission_level(permission_level):
        """检查权限等级是否合法：0，1，2"""
        if permission_level not in [0, 1, 2]:
            return "权限等级必须是 0、1 或 2"
        return True

    @staticmethod
    def validate_fields(fields):
        """批量验证多个字段的合法性"""
        results = {}
        for field, value in fields.items():
            # 动态调用验证方法
            validate_method = getattr(DataValidator, f"validate_{field}", None)
            if validate_method:
                result = validate_method(value)
                results[field] = result
            else:
                results[field] = f"没有找到字段 {field} 的验证方法"
        return results
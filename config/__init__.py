"""
配置包
包含项目所有配置文件
"""

# 导出配置
try:
    from .camera_config import CAMERA_CONFIG
except ImportError as e:
    print(f"导入配置文件失败: {e}")
    CAMERA_CONFIG = None

__all__ = ["CAMERA_CONFIG"]

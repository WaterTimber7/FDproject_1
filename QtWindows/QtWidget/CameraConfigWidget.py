"""
摄像头配置管理组件
用于管理员界面可视化修改摄像头配置
"""
import json
import os
from typing import Dict, List, Any
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QSpinBox, QLineEdit, QPushButton, QComboBox,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QGroupBox, QScrollArea, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from config.camera_config import CAMERA_CONFIG
from logger import app_logger


class CameraConfigWidget(QWidget):
    """摄像头配置管理组件"""
    
    # 定义配置更新信号，携带最新的配置字典
    config_updated_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_file = os.path.join(os.path.dirname(__file__), "..", "..", "config", "camera_config.py")
        self.current_config = CAMERA_CONFIG.copy()
        self._setup_ui()
        self._load_current_config()

    def _setup_ui(self):
        """设置界面布局"""
        main_layout = QVBoxLayout(self)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # # 1. 摄像头数量配置
        # camera_count_group = QGroupBox("摄像头数量配置")
        # camera_count_layout = QFormLayout(camera_count_group)
        #
        # self.max_cameras_spin = QSpinBox()
        # self.max_cameras_spin.setRange(1, 10)
        # self.max_cameras_spin.setToolTip("设置最大摄像头数量")
        # camera_count_layout.addRow("最大摄像头数量:", self.max_cameras_spin)
        #
        # scroll_layout.addWidget(camera_count_group)

        # 2. 摄像头名称配置
        camera_names_group = QGroupBox("摄像头名称配置")
        camera_names_layout = QVBoxLayout(camera_names_group)

        # 摄像头名称列表
        self.camera_list = QListWidget()
        self.camera_list.setMaximumHeight(200)
        camera_names_layout.addWidget(QLabel("摄像头名称列表:"))
        camera_names_layout.addWidget(self.camera_list)

        # 添加/编辑摄像头名称
        name_edit_layout = QHBoxLayout()
        self.camera_index_spin = QSpinBox()
        self.camera_index_spin.setRange(0, 9)
        self.camera_index_spin.setToolTip("摄像头索引")

        self.camera_name_edit = QLineEdit()
        self.camera_name_edit.setPlaceholderText("输入摄像头名称")

        self.add_name_btn = QPushButton("添加/更新")
        self.add_name_btn.clicked.connect(self._add_or_update_camera_name)

        self.remove_name_btn = QPushButton("删除")
        self.remove_name_btn.clicked.connect(self._remove_camera_name)

        name_edit_layout.addWidget(QLabel("索引:"))
        name_edit_layout.addWidget(self.camera_index_spin)
        name_edit_layout.addWidget(QLabel("名称:"))
        name_edit_layout.addWidget(self.camera_name_edit)
        name_edit_layout.addWidget(self.add_name_btn)
        name_edit_layout.addWidget(self.remove_name_btn)

        camera_names_layout.addLayout(name_edit_layout)
        scroll_layout.addWidget(camera_names_group)

        # 3. 权限配置
        permission_group = QGroupBox("权限配置")
        permission_layout = QVBoxLayout(permission_group)

        # 权限级别选择
        permission_select_layout = QHBoxLayout()
        permission_select_layout.addWidget(QLabel("权限级别:"))
        self.permission_combo = QComboBox()
        self.permission_combo.addItems(["0 - 区域0", "1 - 区域1", "2 - 区域",
                                        "3 - 区域3", "4 - 区域4"])
        self.permission_combo.currentIndexChanged.connect(self._load_permission_config)
        permission_select_layout.addWidget(self.permission_combo)
        permission_layout.addLayout(permission_select_layout)

        # 权限对应的摄像头列表
        self.permission_camera_list = QListWidget()
        self.permission_camera_list.setMaximumHeight(150)
        permission_layout.addWidget(QLabel("允许查看的摄像头:"))
        permission_layout.addWidget(self.permission_camera_list)

        # 权限编辑按钮
        permission_edit_layout = QHBoxLayout()
        self.add_permission_btn = QPushButton("添加摄像头")
        self.add_permission_btn.clicked.connect(self._add_camera_to_permission)

        self.remove_permission_btn = QPushButton("移除摄像头")
        self.remove_permission_btn.clicked.connect(self._remove_camera_from_permission)

        permission_edit_layout.addWidget(self.add_permission_btn)
        permission_edit_layout.addWidget(self.remove_permission_btn)
        permission_layout.addLayout(permission_edit_layout)

        scroll_layout.addWidget(permission_group)

        # 4. 操作按钮
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存配置")
        self.save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()

        scroll_layout.addLayout(button_layout)

        # 设置滚动区域
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

    def _load_current_config(self):
        """加载当前配置到界面"""
        # 加载摄像头名称
        self._update_camera_names_list()

        # 加载权限配置
        self._load_permission_config()

    def _update_camera_names_list(self):
        """更新摄像头名称列表显示"""
        self.camera_list.clear()
        for index, name in sorted(self.current_config["camera_names"].items()):
            item = QListWidgetItem(f"索引 {index}: {name}")
            item.setData(Qt.UserRole, index)
            self.camera_list.addItem(item)

    def _load_permission_config(self):
        """加载权限配置"""
        permission_level = self.permission_combo.currentIndex()
        self.permission_camera_list.clear()

        if permission_level in self.current_config["permission_config"]:
            camera_indices = self.current_config["permission_config"][permission_level]
            for index in camera_indices:
                name = self.current_config["camera_names"].get(index, f"摄像头{index}")
                item = QListWidgetItem(f"索引 {index}: {name}")
                item.setData(Qt.UserRole, index)
                self.permission_camera_list.addItem(item)

    def _add_or_update_camera_name(self):
        """添加或更新摄像头名称"""
        index = self.camera_index_spin.value()
        name = self.camera_name_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "警告", "请输入摄像头名称")
            return

        self.current_config["camera_names"][index] = name
        self._update_camera_names_list()
        self.camera_name_edit.clear()
        app_logger.info(f"更新摄像头名称: 索引{index} -> {name}")

    def _remove_camera_name(self):
        """删除摄像头名称"""
        current_item = self.camera_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的摄像头")
            return

        index = current_item.data(Qt.UserRole)
        if index in self.current_config["camera_names"]:
            del self.current_config["camera_names"][index]
            self._update_camera_names_list()
            app_logger.info(f"删除摄像头名称: 索引{index}")

    def _add_camera_to_permission(self):
        """添加摄像头到权限"""
        permission_level = self.permission_combo.currentIndex()
        index = self.camera_index_spin.value()

        if permission_level not in self.current_config["permission_config"]:
            self.current_config["permission_config"][permission_level] = []

        if index not in self.current_config["permission_config"][permission_level]:
            self.current_config["permission_config"][permission_level].append(index)
            self.current_config["permission_config"][permission_level].sort()
            self._load_permission_config()
            app_logger.info(f"添加摄像头到权限{permission_level}: 索引{index}")

    def _remove_camera_from_permission(self):
        """从权限中移除摄像头"""
        current_item = self.permission_camera_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要移除的摄像头")
            return

        permission_level = self.permission_combo.currentIndex()
        index = current_item.data(Qt.UserRole)

        if (permission_level in self.current_config["permission_config"] and
                index in self.current_config["permission_config"][permission_level]):
            self.current_config["permission_config"][permission_level].remove(index)
            self._load_permission_config()
            app_logger.info(f"从权限{permission_level}移除摄像头: 索引{index}")

    def _save_config(self):
        """保存配置到文件"""
        try:
            # ====== 关键修复：同步 permission_config ======
            # 1. 提取当前所有真实存在的摄像头索引
            valid_indices = list(self.current_config["camera_names"].keys())
            
            # 2. 清洗旧的权限列表：删除不在 camera_names 中的废弃索引
            for level in self.current_config["permission_config"]:
                old_list = self.current_config["permission_config"][level]
                # 过滤掉不在 valid_indices 中的索引
                self.current_config["permission_config"][level] = [idx for idx in old_list if idx in valid_indices]
            
            # 3. 把新加的索引授权给所有权限级别
            # 找出所有权限级别中已经有的索引
            all_assigned = set()
            for level in self.current_config["permission_config"]:
                all_assigned.update(self.current_config["permission_config"][level])
            
            # 找出新增的索引（存在于 camera_names 但不在任何权限列表中）
            new_indices = set(valid_indices) - all_assigned
            
            # 将新索引添加到所有权限级别
            if new_indices:
                for level in self.current_config["permission_config"]:
                    for new_idx in new_indices:
                        if new_idx not in self.current_config["permission_config"][level]:
                            self.current_config["permission_config"][level].append(new_idx)
                    # 排序
                    self.current_config["permission_config"][level].sort()
            
            print(f"[配置同步] valid_indices={valid_indices}")
            print(f"[配置同步] permission_config={self.current_config['permission_config']}")
            # ====== 同步结束 ======

            # 生成配置文件内容
            config_content = f'''"""
摄像头配置文件
包含摄像头权限配置和摄像头名称映射
"""

# 摄像头基本配置
CAMERA_CONFIG = {{

    # 摄像头名称映射 (索引: 名称)
    "camera_names": {{
{self._format_camera_names()}
    }},

    # 权限配置 (权限级别: 允许查看的摄像头索引列表)
    "permission_config": {{
{self._format_permission_config()}
    }}
}}
'''

            # 写入文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)

            QMessageBox.information(self, "成功", "配置保存成功！\n检测界面将实时更新。")
            app_logger.info("摄像头配置保存成功")
            
            # 构建最新的配置字典并发射信号
            latest_config = {
                "camera_names": dict(self.current_config["camera_names"]),
                "permission_config": dict(self.current_config["permission_config"])
            }
            self.config_updated_signal.emit(latest_config)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
            app_logger.error(f"保存摄像头配置失败: {e}")

    def _format_camera_names(self):
        """格式化摄像头名称配置"""
        lines = []
        for index, name in sorted(self.current_config["camera_names"].items()):
            lines.append(f'        {index}: "{name}",')
        return '\n'.join(lines)

    def _format_permission_config(self):
        """格式化权限配置"""
        lines = []
        for level, indices in sorted(self.current_config["permission_config"].items()):
            lines.append(f'        {level}: {indices},  # 权限{level}')
        return '\n'.join(lines)

    # _reset_config 和 _reload_config 方法已删除（不再需要）
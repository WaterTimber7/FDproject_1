#!/usr/bin/env python3
"""
现代扁平化风格全局 QSS 样式表
参考 Element Plus / Ant Design 的简洁设计语言
"""

MODERN_QSS = """
/* ==================== 全局基础样式 ==================== */
QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 14px;
}

QMainWindow {
    background-color: #F5F7FA;
}

/* ==================== 滚动条样式 ==================== */
QScrollBar:vertical {
    width: 8px;
    background: transparent;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #C0C4CC;
    border-radius: 4px;
    min-height: 50px;
}

QScrollBar::handle:vertical:hover {
    background: #909399;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    height: 8px;
    background: transparent;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #C0C4CC;
    border-radius: 4px;
    min-width: 50px;
}

QScrollBar::handle:horizontal:hover {
    background: #909399;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ==================== 输入框样式 ==================== */
QLineEdit, QSpinBox, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #DCDFE6;
    border-radius: 4px;
    padding: 0 12px;
    min-height: 32px;
    color: #606266;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #409EFF;
}

QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
    border: 1px solid #C0C4CC;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #C0C4CC;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #DCDFE6;
    border-radius: 4px;
    selection-background-color: #ECF5FF;
    selection-color: #409EFF;
}

/* ==================== 按钮样式 ==================== */
QPushButton {
    background-color: #409EFF;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 0 15px;
    min-height: 32px;
    font-weight: normal;
}

QPushButton:hover {
    background-color: #66B1FF;
}

QPushButton:pressed {
    background-color: #3A8EE6;
}

QPushButton:disabled {
    background-color: #C0C4CC;
    color: #FFFFFF;
}

/* 主按钮 - 登录等（蓝色） */
QPushButton#loginButton, QPushButton#primaryButton {
    background-color: #409EFF;
    font-size: 16px;
    font-weight: bold;
}

QPushButton#loginButton:hover, QPushButton#primaryButton:hover {
    background-color: #66B1FF;
}

QPushButton#loginButton:pressed, QPushButton#primaryButton:pressed {
    background-color: #3A8EE6;
}

/* 危险按钮 - 退出等 */
QPushButton#quitButton, QPushButton#dangerButton {
    background-color: #F56C6C;
}

QPushButton#quitButton:hover, QPushButton#dangerButton:hover {
    background-color: #F78989;
}

QPushButton#quitButton:pressed, QPushButton#dangerButton:pressed {
    background-color: #DD6161;
}

/* ==================== 分组框样式 ==================== */
QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E4E7ED;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #303133;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: #409EFF;
}

/* ==================== 表格样式 ==================== */
QTableWidget, QTableView {
    background-color: #FFFFFF;
    border: 1px solid #E4E7ED;
    border-radius: 8px;
    gridline-color: #EBEEF5;
    selection-background-color: #ECF5FF;
    selection-color: #409EFF;
}

QTableWidget::item, QTableView::item {
    padding: 8px;
    border-bottom: 1px solid #EBEEF5;
}

QHeaderView::section {
    background-color: #F5F7FA;
    color: #606266;
    font-weight: bold;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #409EFF;
}

QHeaderView::section:last {
    border-right: none;
}

/* ==================== 列表样式 ==================== */
QListWidget, QListView {
    background-color: #FFFFFF;
    border: 1px solid #E4E7ED;
    border-radius: 8px;
    padding: 5px;
}

QListWidget::item, QListView::item {
    padding: 10px;
    border-bottom: 1px solid #F5F7FA;
}

QListWidget::item:hover, QListView::item:hover {
    background-color: #F5F7FA;
}

QListWidget::item:selected, QListView::item:selected {
    background-color: #ECF5FF;
    color: #409EFF;
}

/* ==================== 标签样式 ==================== */
QLabel {
    color: #606266;
    background: transparent;
}

/* ==================== 堆叠窗口容器 ==================== */
QStackedWidget > QWidget {
    background-color: #FFFFFF;
    border-radius: 8px;
}

/* ==================== 消息提示 ==================== */
QMessageBox {
    background-color: #FFFFFF;
}

QMessageBox QLabel {
    color: #606266;
    font-size: 14px;
}

/* ==================== 进度条 ==================== */
QProgressBar {
    background-color: #F5F7FA;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #606266;
}

QProgressBar::chunk {
    background-color: #409EFF;
    border-radius: 4px;
}
"""
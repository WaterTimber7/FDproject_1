import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class CellWidget(QWidget):
    def __init__(self, content, index, grid_layout, main_window):
        super().__init__()
        self.index = index
        self.grid_layout = grid_layout
        self.main_window = main_window
        self.is_fullscreen = False

        # 主布局
        main_vlayout = QVBoxLayout()
        main_vlayout.setContentsMargins(0, 0, 0, 0)

        # 标题栏（包含按钮和标签）
        title_bar = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(5, 0, 5, 0)

        # 区域标签
        title_label = QLabel(content.split('\n')[0])
        title_label.setStyleSheet("font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # 全屏/恢复按钮（仅非左上角区域显示）
        self.toggle_btn = QPushButton("□")
        self.toggle_btn.setFixedSize(20, 20)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid #aaa;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #888;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_fullscreen)

        # 左上角区域(索引0)不显示全屏按钮
        if index != 0:
            title_layout.addWidget(self.toggle_btn)
        else:
            # 左上角区域显示固定标识
            fixed_label = QLabel("固定区域")
            fixed_label.setStyleSheet("color: #888; font-size: 10px;")
            title_layout.addWidget(fixed_label)

        title_bar.setLayout(title_layout)

        # 内容区域
        self.content_label = QLabel(content)
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setStyleSheet("""
            QLabel {
                background-color: rgba(240, 240, 240, 100);
                border: 1px solid #ccc;
                font-size: 14px;
                border-radius: 3px;
            }
        """)

        # 将标题栏和内容添加到主布局
        main_vlayout.addWidget(title_bar)
        main_vlayout.addWidget(self.content_label, 1)

        self.setLayout(main_vlayout)
        self.apply_color_scheme()

        # 保存原始位置信息
        self.original_position = None
        self.siblings_info = []

    def apply_color_scheme(self):
        """为每个区域应用不同的背景色"""
        colors = [
            "rgba(173, 216, 230, 100)",  # 浅蓝色
            "rgba(144, 238, 144, 100)",  # 浅绿色
            "rgba(255, 182, 193, 100)",  # 浅粉色
            "rgba(255, 255, 224, 100)"  # 浅黄色
        ]
        style = f"""
            QWidget {{
                background-color: {colors[self.index]};
                border: 2px solid {colors[self.index].replace('100', '200')};
                border-radius: 5px;
            }}
        """
        self.setStyleSheet(style)

    def toggle_fullscreen(self):
        """切换全屏/恢复状态"""
        if not self.is_fullscreen:
            self.enter_fullscreen()
        else:
            self.exit_fullscreen()

    def enter_fullscreen(self):
        """进入全屏模式"""
        self.is_fullscreen = True
        self.toggle_btn.setText("◱")

        # 保存当前布局状态信息
        self.save_current_layout_state()

        # 隐藏其他widget
        for info in self.siblings_info:
            info['widget'].hide()

        # 当前widget占据整个布局
        self.grid_layout.addWidget(self, 0, 0, 4, 4)  # 占据4x4网格的所有空间

        # 更新按钮状态
        self.update_sibling_buttons(False)

        # 更新主窗口状态
        self.main_window.update_status(f"区域 {self.index + 1} 已全屏显示")

    def exit_fullscreen(self):
        """退出全屏模式"""
        self.is_fullscreen = False
        self.toggle_btn.setText("□")

        # 从布局中移除当前widget
        self.grid_layout.removeWidget(self)

        # 恢复其他widget
        for info in self.siblings_info:
            widget = info['widget']
            widget.show()
            self.grid_layout.addWidget(widget,
                                       info['row'],
                                       info['col'],
                                       info['row_span'],
                                       info['col_span'])

        # 恢复当前widget到原始位置
        if self.original_position:
            self.grid_layout.addWidget(self,
                                       self.original_position['row'],
                                       self.original_position['col'],
                                       self.original_position['row_span'],
                                       self.original_position['col_span'])

        # 更新按钮状态
        self.update_sibling_buttons(True)

        # 清除信息
        self.original_position = None
        self.siblings_info = []

        # 更新主窗口状态
        self.main_window.update_status("已恢复原始布局")

    def save_current_layout_state(self):
        """保存当前布局状态"""
        # 保存当前widget的位置信息
        index = self.grid_layout.indexOf(self)
        if index >= 0:
            row, col, row_span, col_span = self.grid_layout.getItemPosition(index)
            self.original_position = {
                'row': row,
                'col': col,
                'row_span': row_span,
                'col_span': col_span
            }

        # 收集其他widget的信息
        self.siblings_info = []
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if item and item.widget() and item.widget() != self:
                widget = item.widget()
                # 获取widget在布局中的位置信息
                index = self.grid_layout.indexOf(widget)
                row, col, row_span, col_span = self.grid_layout.getItemPosition(index)

                self.siblings_info.append({
                    'widget': widget,
                    'row': row,
                    'col': col,
                    'row_span': row_span,
                    'col_span': col_span
                })

    def update_sibling_buttons(self, enabled):
        """更新其他区域的按钮状态"""
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if item and item.widget() and item.widget() != self:
                widget = item.widget()
                if hasattr(widget, 'toggle_btn'):
                    widget.toggle_btn.setEnabled(enabled)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cells = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('固定比例四区域展示窗口')
        self.setGeometry(100, 100, 1000, 700)

        # 中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 创建4x4网格布局以实现精确比例控制
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)

        # 定义区域配置：每个区域由(row, col, row_span, col_span)定义
        # 使用4x4网格实现精确的3:1比例
        area_configs = [
            # 区域1: 左上角，占1/4宽度，3/4高度
            (0, 0, 3, 1),
            # 区域2: 右上角，占3/4宽度，3/4高度
            (0, 1, 3, 3),
            # 区域3: 左下角，占1/4宽度，1/4高度
            (3, 0, 1, 1),
            # 区域4: 右下角，占3/4宽度，1/4高度
            (3, 1, 1, 3)
        ]

        # 创建4个区域
        contents = [
            "区域 1\n左上\n(固定区域)",
            "区域 2\n右上\n(占3/4宽度，3/4高度)",
            "区域 3\n左下\n(占1/4宽度，1/4高度)",
            "区域 4\n右下\n(占3/4宽度，1/4高度)"
        ]

        # 创建并添加各个区域
        for i, (row, col, row_span, col_span) in enumerate(area_configs):
            cell = CellWidget(contents[i], i, self.grid_layout, self)
            self.grid_layout.addWidget(cell, row, col, row_span, col_span)
            self.cells.append(cell)

        # 设置网格布局的行列比例以保持3:1比例
        # 使用4行4列，其中：
        # - 行0-2: 3/4高度 (每行权重为1，共3)
        # - 行3: 1/4高度 (权重为1)
        # - 列0: 1/4宽度 (权重为1)
        # - 列1-3: 3/4宽度 (每列权重为1，共3)

        # 设置行权重
        for row in range(4):
            if row < 3:  # 前3行共享3/4高度
                self.grid_layout.setRowStretch(row, 3)
            else:  # 第4行占1/4高度
                self.grid_layout.setRowStretch(row, 1)

        # 设置列权重
        for col in range(4):
            if col == 0:  # 第1列占1/4宽度
                self.grid_layout.setColumnStretch(col, 1)
            else:  # 后3列共享3/4宽度
                self.grid_layout.setColumnStretch(col, 3)

        # 将网格布局添加到主布局
        main_layout.addLayout(self.grid_layout, 1)  # 1表示拉伸因子

        # 底部控制面板
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)

        # 布局说明
        layout_info = QLabel("固定比例布局: 右侧占3/4宽度 | 上方占3/4高度 | 拖动窗口时比例不变")
        layout_info.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        bottom_layout.addWidget(layout_info)

        bottom_layout.addStretch()

        # 比例显示
        self.ratio_label = QLabel("当前比例: 3:1")
        self.ratio_label.setStyleSheet("color: #2c3e50; font-weight: bold; padding: 5px;")
        bottom_layout.addWidget(self.ratio_label)

        bottom_layout.addSpacing(20)

        # 重置按钮
        reset_btn = QPushButton("重置布局")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        reset_btn.clicked.connect(self.reset_layout)
        bottom_layout.addWidget(reset_btn)

        main_layout.addWidget(bottom_panel)

        central_widget.setLayout(main_layout)

        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪 - 拖动窗口可查看固定比例效果")

        # 定时器用于更新窗口大小信息
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.update_window_info)
        self.resize_timer.start(100)  # 每100ms更新一次

    def reset_layout(self):
        """重置所有区域到原始布局"""
        for cell in self.cells:
            if cell.is_fullscreen:
                cell.exit_fullscreen()
        self.update_status("已重置所有区域")

    def update_status(self, message):
        """更新状态栏信息"""
        self.status_bar.showMessage(message)

    def update_window_info(self):
        """更新窗口信息"""
        size = self.size()
        width_ratio = self.cells[1].width() / self.cells[0].width() if self.cells[0].width() > 0 else 0
        height_ratio = self.cells[0].height() / self.cells[2].height() if self.cells[2].height() > 0 else 0

        width_info = f"宽: {size.width()}px"
        height_info = f"高: {size.height()}px"
        ratio_info = f"宽比: {width_ratio:.2f}:1 | 高比: {height_ratio:.2f}:1"

        self.setWindowTitle(f'固定比例四区域展示窗口 - {width_info} | {height_info}')
        self.ratio_label.setText(f"当前比例: {ratio_info}")

    def resizeEvent(self, event):
        """窗口大小改变时确保比例不变"""
        super().resizeEvent(event)

        # 强制布局更新
        self.grid_layout.invalidate()
        self.grid_layout.activate()

        # 计算并显示当前比例
        width = self.width()
        height = self.height()

        # 理想比例：右侧占3/4，上方占3/4
        right_width = width * 3 // 4
        left_width = width - right_width
        top_height = height * 3 // 4
        bottom_height = height - top_height

        # 在状态栏显示信息
        self.status_bar.showMessage(
            f"窗口: {width}×{height} | 左侧宽: {left_width}px | 右侧宽: {right_width}px | 上方高: {top_height}px | 下方高: {bottom_height}px")

    def closeEvent(self, event):
        """关闭窗口时停止定时器"""
        self.resize_timer.stop()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    # 设置全局样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f7fa;
        }
        QLabel {
            color: #2c3e50;
        }
    """)

    # 设置字体
    font = QFont("微软雅黑", 10)
    app.setFont(font)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
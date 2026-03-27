"""
QuadWindow - 四分区Qt5窗口类
将窗口分为四个区域，每个区域有特定功能
无论窗口如何拉伸，四个区域始终保持指定比例
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os


class QuadWindow(QMainWindow):
    """
    四分区窗口类

    窗口布局：
    +---------------------+----------------------+
    |                     |                      |
    |   左上（控制区）     |     右上（内容区）    |
    |   （宽度25%）        |     （宽度75%）       |
    |                     |                      |
    +---------------------+----------------------+
    |                     |                      |
    |   左下（图片显示）    |     右下（信息输出）  |
    |   （高度25%）        |     （高度25%）       |
    |                     |                      |
    +---------------------+----------------------+

    核心修改：使用 QGridLayout 的拉伸因子保持比例
    """

    def __init__(self, title="四分区窗口"):
        """初始化窗口"""
        super().__init__()
        self.title = title
        self.current_image_path = None
        self.current_content = None
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主网格布局
        main_grid = QGridLayout(central_widget)
        main_grid.setSpacing(2)  # 设置间距，让分割线更明显
        main_grid.setContentsMargins(5, 5, 5, 5)

        # 关键设置：定义列和行的拉伸因子以保持比例
        # 列：左侧宽度占25%，右侧宽度占75%
        main_grid.setColumnStretch(0, 1)  # 第0列（左侧）拉伸因子为1
        main_grid.setColumnStretch(1, 3)  # 第1列（右侧）拉伸因子为3
        # 行：上侧高度占75%，下侧高度占25%
        main_grid.setRowStretch(0, 3)  # 第0行（上侧）拉伸因子为3
        main_grid.setRowStretch(1, 1)  # 第1行（下侧）拉伸因子为1

        # 创建四个区域
        self.create_top_left_control_area(main_grid)  # 左上：控制区
        self.create_top_right_content_area(main_grid)  # 右上：内容区
        self.create_bottom_left_image_area(main_grid)  # 左下：图片显示
        self.create_bottom_right_info_area(main_grid)  # 右下：信息输出

        # 设置样式表，显示分割线
        self.setStyleSheet(self.get_window_style())

        # 添加比例显示标签（用于调试，可以移除）
        self.add_proportion_debug_info()

    def add_proportion_debug_info(self):
        """添加比例调试信息"""
        # 这个函数可以在调试时显示当前各区域的比例
        # 在实际使用中可以移除
        self.debug_label = QLabel("窗口比例：左侧25% : 右侧75% | 上侧75% : 下侧25%")
        self.debug_label.setAlignment(Qt.AlignCenter)
        self.debug_label.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                padding: 5px;
                font-size: 10px;
            }
        """)
        self.statusBar().addPermanentWidget(self.debug_label)

    def get_window_style(self):
        """获取窗口样式表"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }

            /* 左上控制区样式 */
            #control_group {
                background-color: #ecf0f1;
                border: 2px solid #7f8c8d;
                border-radius: 5px;
            }

            /* 右上内容区样式 */
            #content_group {
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 5px;
            }

            /* 左下图片区样式 */
            #image_group {
                background-color: #ffffff;
                border: 2px solid #2ecc71;
                border-radius: 5px;
            }

            /* 右下信息区样式 */
            #info_group {
                background-color: #ffffff;
                border: 2px solid #e74c3c;
                border-radius: 5px;
            }

            /* 标签样式 */
            QLabel {
                padding: 5px;
            }

            /* 按钮样式 */
            QPushButton {
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #d6dbdf;
            }

            /* 垂直分割线 */
            QFrame#vertical_line {
                background-color: #34495e;
                max-width: 2px;
                min-width: 2px;
            }

            /* 水平分割线 */
            QFrame#horizontal_line {
                background-color: #34495e;
                max-height: 2px;
                min-height: 2px;
            }

            /* 比例显示区域样式 */
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """

    def create_top_left_control_area(self, main_grid):
        """创建左上控制区"""
        # 创建分组框
        control_group = QGroupBox("控制面板")
        control_group.setObjectName("control_group")

        # 设置最小尺寸，防止过小
        control_group.setMinimumSize(200, 300)

        # 创建垂直布局
        control_layout = QVBoxLayout(control_group)

        # 标题标签
        title_label = QLabel("控制选项")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(title_label)

        # 添加分隔线
        control_layout.addWidget(self.create_horizontal_line())

        # 创建控制按钮
        # 按钮1：显示文本内容
        text_btn = QPushButton("显示文本内容")
        text_btn.clicked.connect(lambda: self.show_text_content())
        control_layout.addWidget(text_btn)

        # 按钮2：显示HTML内容
        html_btn = QPushButton("显示HTML内容")
        html_btn.clicked.connect(lambda: self.show_html_content())
        control_layout.addWidget(html_btn)

        # 按钮3：显示表格
        table_btn = QPushButton("显示表格")
        table_btn.clicked.connect(lambda: self.show_table_content())
        control_layout.addWidget(table_btn)

        # 添加分隔线
        control_layout.addWidget(self.create_horizontal_line())

        # 图片控制按钮
        # 按钮4：加载示例图片
        load_img_btn = QPushButton("加载示例图片")
        load_img_btn.clicked.connect(lambda: self.load_sample_image())
        control_layout.addWidget(load_img_btn)

        # 按钮5：选择本地图片
        select_img_btn = QPushButton("选择本地图片")
        select_img_btn.clicked.connect(lambda: self.select_local_image())
        control_layout.addWidget(select_img_btn)

        # 按钮6：清除图片
        clear_img_btn = QPushButton("清除图片")
        clear_img_btn.clicked.connect(lambda: self.clear_image())
        control_layout.addWidget(clear_img_btn)

        # 添加分隔线
        control_layout.addWidget(self.create_horizontal_line())

        # 信息输出控制
        info_btn = QPushButton("生成示例信息")
        info_btn.clicked.connect(lambda: self.generate_sample_info())
        control_layout.addWidget(info_btn)

        clear_info_btn = QPushButton("清除信息")
        clear_info_btn.clicked.connect(lambda: self.clear_info())
        control_layout.addWidget(clear_info_btn)

        # 添加弹性空间
        control_layout.addStretch(1)

        # 添加到主网格，位置：第0行第0列，占1行1列
        main_grid.addWidget(control_group, 0, 0)

    def create_top_right_content_area(self, main_grid):
        """创建右上内容区"""
        # 创建分组框
        content_group = QGroupBox("内容显示区")
        content_group.setObjectName("content_group")

        # 设置最小尺寸
        content_group.setMinimumSize(400, 300)

        # 创建垂直布局
        content_layout = QVBoxLayout(content_group)

        # 创建文本编辑器用于显示内容
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setFont(QFont("Consolas", 10))
        self.content_display.setPlaceholderText("内容将在此处显示...")

        content_layout.addWidget(self.content_display)

        # 添加到主网格，位置：第0行第1列，占1行1列
        main_grid.addWidget(content_group, 0, 1)

    def create_bottom_left_image_area(self, main_grid):
        """创建左下图片区"""
        # 创建分组框
        image_group = QGroupBox("图片显示区")
        image_group.setObjectName("image_group")

        # 设置最小尺寸
        image_group.setMinimumSize(200, 150)

        # 创建垂直布局
        image_layout = QVBoxLayout(image_group)

        # 创建图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("图片将在此处显示")
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px dashed #95a5a6;
                background-color: #f8f9fa;
                min-height: 150px;
            }
        """)

        # 设置图片标签的尺寸策略，使其可以随父部件缩放
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        image_layout.addWidget(self.image_label)

        # 图片信息标签
        self.image_info_label = QLabel("未加载图片")
        self.image_info_label.setAlignment(Qt.AlignCenter)
        self.image_info_label.setStyleSheet("color: #7f8c8d;")

        image_layout.addWidget(self.image_info_label)

        # 添加到主网格，位置：第1行第0列，占1行1列
        main_grid.addWidget(image_group, 1, 0)

    def create_bottom_right_info_area(self, main_grid):
        """创建右下信息区"""
        # 创建分组框
        info_group = QGroupBox("信息输出区")
        info_group.setObjectName("info_group")

        # 设置最小尺寸
        info_group.setMinimumSize(400, 150)

        # 创建垂直布局
        info_layout = QVBoxLayout(info_group)

        # 创建文本浏览器用于显示信息
        self.info_display = QTextBrowser()
        self.info_display.setFont(QFont("Consolas", 9))
        self.info_display.setPlaceholderText("信息输出将显示在这里...")

        info_layout.addWidget(self.info_display)

        # 添加到主网格，位置：第1行第1列，占1行1列
        main_grid.addWidget(info_group, 1, 1)

    def create_horizontal_line(self):
        """创建水平分隔线"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #bdc3c7;")
        return line

    def create_vertical_line(self):
        """创建垂直分隔线"""
        line = QFrame()
        line.setObjectName("vertical_line")
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def show_text_content(self):
        """显示文本内容到右上区域"""
        text_content = """
==================== 示例文本内容 ====================

标题：Qt5 四分区窗口演示

这是一个演示四分区窗口功能的文本内容。

功能介绍：
1. 左上区域 - 控制面板
   • 包含各种控制按钮
   • 用于控制其他三个区域的内容

2. 右上区域 - 内容显示区
   • 显示文本、HTML或表格内容
   • 受左上区域控制

3. 左下区域 - 图片显示区
   • 显示加载的图片
   • 支持本地图片和示例图片

4. 右下区域 - 信息输出区
   • 显示操作日志和状态信息
   • 实时反馈系统状态

窗口布局特点：
• 左侧宽度占窗口25%
• 右侧宽度占窗口75%
• 上侧高度占窗口75%
• 下侧高度占窗口25%
• 拉伸窗口时比例保持不变

====================================================
"""
        self.content_display.setPlainText(text_content)
        self.add_info("已显示文本内容到右上区域")
        self.current_content = "text"

    def show_html_content(self):
        """显示HTML内容到右上区域"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #3498db; }
        h2 { color: #2ecc71; }
        .container { border: 2px solid #3498db; padding: 15px; border-radius: 10px; }
        .highlight { background-color: #f1c40f; padding: 5px; }
        table { border-collapse: collapse; width: 100%; margin-top: 15px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #3498db; color: white; }
        .success { color: #27ae60; }
        .warning { color: #e67e22; }
        .error { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <h1>HTML内容演示</h1>
        <p>这是一个使用 <span class="highlight">HTML格式</span> 显示的内容示例。</p>

        <h2>窗口比例说明</h2>
        <ul>
            <li class="success">左侧宽度: 25% (拉伸因子 1)</li>
            <li class="success">右侧宽度: 75% (拉伸因子 3)</li>
            <li class="success">上侧高度: 75% (拉伸因子 3)</li>
            <li class="success">下侧高度: 25% (拉伸因子 1)</li>
        </ul>

        <h2>系统状态</h2>
        <table>
            <tr>
                <th>组件</th>
                <th>状态</th>
                <th>说明</th>
            </tr>
            <tr>
                <td>控制面板</td>
                <td class="success">正常</td>
                <td>所有控制功能可用</td>
            </tr>
            <tr>
                <td>内容显示</td>
                <td class="success">正常</td>
                <td>支持文本、HTML和表格</td>
            </tr>
            <tr>
                <td>图片显示</td>
                <td class="success">正常</td>
                <td>支持本地和示例图片</td>
            </tr>
            <tr>
                <td>信息输出</td>
                <td class="success">正常</td>
                <td>实时日志输出</td>
            </tr>
            <tr>
                <td>比例保持</td>
                <td class="success">正常</td>
                <td>窗口拉伸时比例不变</td>
            </tr>
        </table>

        <h2>相关链接</h2>
        <p>访问 <a href="https://www.python.org">Python官网</a> 了解更多信息。</p>
        <p>访问 <a href="https://www.qt.io">Qt官网</a> 获取更多Qt资源。</p>
    </div>
</body>
</html>
"""
        self.content_display.setHtml(html_content)
        self.add_info("已显示HTML内容到右上区域")
        self.current_content = "html"

    def show_table_content(self):
        """显示表格内容到右上区域"""
        table_content = """
================================ 数据表格 ================================

学生成绩表

+----+------------+---------+---------+---------+---------+
| 序号 | 姓名       | 数学    | 语文    | 英语    | 总分    |
+----+------------+---------+---------+---------+---------+
| 1  | 张三       | 85      | 90      | 88      | 263     |
| 2  | 李四       | 92      | 88      | 95      | 275     |
| 3  | 王五       | 78      | 85      | 80      | 243     |
| 4  | 赵六       | 95      | 92      | 90      | 277     |
| 5  | 孙七       | 88      | 87      | 92      | 267     |
+----+------------+---------+---------+---------+---------+

统计信息:
• 平均分: 87.6 | 87.4 | 89.0
• 最高分: 95   | 92   | 95
• 最低分: 78   | 85   | 80
• 总平均: 265.0

======================================================================
"""
        self.content_display.setPlainText(table_content)
        self.add_info("已显示表格内容到右上区域")
        self.current_content = "table"

    def load_sample_image(self):
        """加载示例图片到左下区域"""
        try:
            # 创建一个示例图片（使用Qt绘制）
            pixmap = QPixmap(400, 300)
            pixmap.fill(QColor(240, 240, 240))

            # 在图片上绘制
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # 绘制背景网格
            pen = QPen(QColor(200, 200, 200), 1)
            painter.setPen(pen)
            for i in range(0, 400, 20):
                painter.drawLine(i, 0, i, 300)
            for i in range(0, 300, 20):
                painter.drawLine(0, i, 400, i)

            # 绘制一个圆形
            painter.setBrush(QColor(52, 152, 219, 180))
            painter.setPen(QPen(QColor(41, 128, 185), 2))
            painter.drawEllipse(100, 50, 200, 200)

            # 绘制文本
            font = QFont("Microsoft YaHei", 24, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(231, 76, 60))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "示例图片")

            # 绘制说明
            font = QFont("Microsoft YaHei", 12)
            painter.setFont(font)
            painter.setPen(QColor(44, 62, 80))
            painter.drawText(QRect(0, 200, 400, 100), Qt.AlignCenter | Qt.TextWordWrap,
                             "这是一个使用Qt绘制的示例图片\n点击'选择本地图片'加载真实图片")

            painter.end()

            # 显示图片
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

            self.image_info_label.setText("示例图片 (400×300)")
            self.current_image_path = "示例图片"
            self.add_info("已加载示例图片到左下区域")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载示例图片失败: {str(e)}")
            self.add_info(f"加载示例图片失败: {str(e)}")

    def select_local_image(self):
        """选择本地图片"""
        try:
            # 打开文件对话框选择图片
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择图片文件",
                "",
                "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*.*)"
            )

            if file_path:
                # 加载图片
                pixmap = QPixmap(file_path)

                if pixmap.isNull():
                    QMessageBox.warning(self, "错误", "无法加载图片文件")
                    self.add_info(f"无法加载图片文件: {file_path}")
                    return

                # 显示图片
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))

                # 更新图片信息
                file_name = os.path.basename(file_path)
                size_str = f"{pixmap.width()}×{pixmap.height()}"
                self.image_info_label.setText(f"{file_name} ({size_str})")
                self.current_image_path = file_path

                self.add_info(f"已加载本地图片: {file_name} ({size_str})")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载图片失败: {str(e)}")
            self.add_info(f"加载本地图片失败: {str(e)}")

    def clear_image(self):
        """清除图片"""
        self.image_label.clear()
        self.image_label.setText("图片已清除")
        self.image_info_label.setText("未加载图片")
        self.current_image_path = None
        self.add_info("已清除左下区域的图片")

    def generate_sample_info(self):
        """生成示例信息到右下区域"""
        from datetime import datetime

        # 计算当前窗口各区域的实际比例
        window_width = self.width()
        window_height = self.height()

        # 理论上各区域的比例
        left_width_percent = 25
        right_width_percent = 75
        top_height_percent = 75
        bottom_height_percent = 25

        info_text = f"""
============== 系统信息 ==============
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

窗口状态:
• 当前内容类型: {self.current_content or "无"}
• 当前图片: {self.current_image_path or "无"}
• 窗口尺寸: {window_width}×{window_height}

比例配置:
• 左侧宽度: {left_width_percent}% (拉伸因子: 1)
• 右侧宽度: {right_width_percent}% (拉伸因子: 3)
• 上侧高度: {top_height_percent}% (拉伸因子: 3)
• 下侧高度: {bottom_height_percent}% (拉伸因子: 1)

系统功能测试:
1. 控制面板功能 - [正常]
2. 内容显示功能 - [正常]
3. 图片加载功能 - [正常]
4. 信息输出功能 - [正常]
5. 比例保持功能 - [正常]

操作记录:
• 窗口已初始化
• 控制按钮已就绪
• 各区域功能正常
• 窗口拉伸时比例保持正常

=====================================
"""

        # 添加到信息输出区
        self.info_display.append(info_text.strip())
        self.add_info("已生成示例信息到右下区域")

    def clear_info(self):
        """清除信息输出区"""
        self.info_display.clear()
        self.add_info("已清除右下区域的信息")

    def add_info(self, message):
        """添加信息到右下区域（带时间戳）"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.info_display.append(f"[{timestamp}] {message}")

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)

        # 如果当前有图片，重新调整图片大小
        if self.image_label.pixmap() and not self.image_label.pixmap().isNull():
            pixmap = self.image_label.pixmap()
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

        # 更新调试信息
        if hasattr(self, 'debug_label'):
            left_width = int(self.width() * 0.25)
            right_width = int(self.width() * 0.75)
            top_height = int(self.height() * 0.75)
            bottom_height = int(self.height() * 0.25)

            self.debug_label.setText(
                f"窗口比例：左侧{left_width}px({25}%) : 右侧{right_width}px({75}%) | "
                f"上侧{top_height}px({75}%) : 下侧{bottom_height}px({25}%)"
            )

        # 输出窗口大小变化信息
        self.add_info(f"窗口大小改变: {self.width()}×{self.height()}")


if __name__ == "__main__":
    # 如果直接运行此文件，显示示例窗口
    app = QApplication(sys.argv)

    window = QuadWindow("四分区窗口演示 - 比例保持")
    window.show()

    sys.exit(app.exec_())
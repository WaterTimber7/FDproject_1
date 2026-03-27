#!/usr/bin/env python3
import sys

from PyQt5.QtWidgets import QApplication

from QtWindows.Windows.AdminLoginWindow import AdminLoginWindow
from QtWindows.UI.modern_theme import MODERN_QSS

def main():
    app = QApplication(sys.argv)
    
    # 应用现代扁平化风格
    app.setStyleSheet(MODERN_QSS)
    
    login_window = AdminLoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
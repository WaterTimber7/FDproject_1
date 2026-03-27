#!/usr/bin/env python3
import sys

from PyQt5.QtWidgets import QApplication

from QtWindows import *

def main():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
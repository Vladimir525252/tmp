import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QProgressBar,
    QComboBox, QCheckBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt

from auth import RegistrationWindow
from app import MainWindow
# from task_manager import *
# from marks_stats import *
# пока закомментировано, потому что классы еще не реализованы
# основной файл, который запускает само приложение
from screeninfo import get_monitors
import data

"""for monitor in get_monitors():
    print(f"{monitor.name} {monitor.width}x{monitor.height}")"""


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = RegistrationWindow()
        window.show()
        sys.exit(app.exec_())
    finally:
        print(data.state, data.email, data.name, data.psw)
        # здесь надо будет отработать с сервером
        data.state, data.email, data.name, data.psw = '', '', '', ''


if __name__ == "__main__":
    main()

import sys
import screeninfo
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QProgressBar,
    QComboBox, QCheckBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from screeninfo import get_monitors
import data

HEIGHT, WIDTH = screeninfo.get_monitors()[0].height, screeninfo.get_monitors()[0].width


# print(HEIGHT, WIDTH)


def load_qss(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def clear_layout(layout):
    if layout is None:
        return
    while layout.count() > 0:
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()  # Освобождаем память
        else:
            clear_layout(item.layout())


class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.log_or_reg = "log"  # чтобы знать, какое окно отображать: вход или регистрация
        self.light_qss = load_qss("modern_light.qss")
        self.dark_qss = load_qss("modern_dark.qss")
        self.setStyleSheet(self.light_qss)
        self.set_ui()

    # UI

    def set_ui(self):
        self.setWindowTitle("Авторизация")
        self.setFixedSize(int(WIDTH * 0.33), int(HEIGHT * 0.7))  # -> проверить размеры

        icon = QIcon('icon.jpg')
        self.setWindowIcon(icon)

        self.root = QHBoxLayout()
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        self.root.addWidget(self.build_content_login(), stretch=1)
        self.setLayout(self.root)

    def build_content_register(self):
        content = QWidget()
        content.setObjectName("content")

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Карточка
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(380)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)

        header = QLabel("Регистрация")
        header.setObjectName("cardHeader")
        card_layout.addWidget(header)
        card_layout.addSpacing(4)

        # Поле "Имя"
        """lbl_name = QLabel("Имя")
        lbl_name.setObjectName("fieldLabel")
        card_layout.addWidget(lbl_name)"""

        self.input_name = QLineEdit()
        self.input_name.setObjectName("inputField")
        self.input_name.setPlaceholderText("ФИО")
        # self.input_name.returnPressed.connect(self.on_name_enter)
        card_layout.addWidget(self.input_name)

        # Поле "Email"
        """lbl_email = QLabel("Email")
        lbl_email.setObjectName("fieldLabel")
        card_layout.addWidget(lbl_email)"""

        self.input_email = QLineEdit()
        self.input_email.setObjectName("inputField")
        self.input_email.setPlaceholderText("Email")
        # self.input_email.returnPressed.connect(self.on_email_enter)
        card_layout.addWidget(self.input_email)
        # Поле "Пароль"
        """lbl_psw = QLabel("Пароль")
        lbl_psw.setObjectName("fieldLabel")
        card_layout.addWidget(lbl_psw)"""

        self.input_psw = QLineEdit()
        self.input_psw.setObjectName("inputField")
        self.input_psw.setPlaceholderText("Пароль")
        # self.input_psw.returnPressed.connect(self.on_psw_enter)
        card_layout.addWidget(self.input_psw)
        """lbl_psw = QLabel("Пароль")
                lbl_psw.setObjectName("fieldLabel")
                card_layout.addWidget(lbl_psw)"""

        self.input_psw_2 = QLineEdit()
        self.input_psw_2.setObjectName("inputField")
        self.input_psw_2.setPlaceholderText("Подтвердите пароль")
        # self.input_psw_2.returnPressed.connect(self.on_psw_2_enter)
        card_layout.addWidget(self.input_psw_2)

        card_layout.addSpacing(4)

        # Чекбокс
        self.checkbox = QCheckBox("Запомнить меня")
        self.checkbox.setObjectName("checkbox")
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        card_layout.addWidget(self.checkbox)
        self.state = False

        card_layout.addSpacing(8)

        # Кнопки действия
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout_2 = QHBoxLayout()
        btn_layout_2.setSpacing(10)

        """self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setObjectName("secondaryButton")
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)
        btn_layout.addWidget(self.btn_cancel)"""

        self.btn_continue = QPushButton("Продолжить")
        self.btn_continue.setObjectName("primaryButton")
        self.btn_continue.clicked.connect(self.on_continue_clicked)
        btn_layout.addWidget(self.btn_continue)

        card_layout.addLayout(btn_layout)

        check_for_acc_label = QLabel("Уже есть аккаунт?")
        check_for_acc_label.setObjectName("fieldLabel")
        card_layout.addWidget(check_for_acc_label)

        self.btn_change = QPushButton("Войти")
        self.btn_change.setObjectName("secondaryButton")
        self.btn_change.clicked.connect(self.on_change_clicked)
        btn_layout_2.addWidget(self.btn_change)

        card_layout.addLayout(btn_layout_2)

        card.setLayout(card_layout)
        layout.addWidget(card, alignment=Qt.AlignHCenter)

        content.setLayout(layout)
        return content

    def build_content_login(self):
        content = QWidget()
        content.setObjectName("content")

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Карточка
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(380)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)

        header = QLabel("Вход в систему")
        header.setObjectName("cardHeader")
        card_layout.addWidget(header)
        card_layout.addSpacing(4)

        # Поле "Имя"
        """lbl_name = QLabel("Имя")
        lbl_name.setObjectName("fieldLabel")
        card_layout.addWidget(lbl_name)"""

        self.input_name = QLineEdit()
        self.input_name.setObjectName("inputField")
        self.input_name.setPlaceholderText("ФИО / email")
        # self.input_name.returnPressed.connect(self.on_name_enter)
        card_layout.addWidget(self.input_name)

        # Поле "Email"
        """lbl_email = QLabel("Email")
        lbl_email.setObjectName("fieldLabel")
        card_layout.addWidget(lbl_email)"""

        # Поле "Пароль"
        """lbl_psw = QLabel("Пароль")
        lbl_psw.setObjectName("fieldLabel")
        card_layout.addWidget(lbl_psw)"""

        self.input_psw = QLineEdit()
        self.input_psw.setObjectName("inputField")
        self.input_psw.setPlaceholderText("Пароль")
        # self.input_psw.returnPressed.connect(self.on_psw_enter)
        card_layout.addWidget(self.input_psw)
        """lbl_psw = QLabel("Пароль")
                lbl_psw.setObjectName("fieldLabel")
                card_layout.addWidget(lbl_psw)"""

        card_layout.addSpacing(4)

        # Чекбокс
        self.checkbox = QCheckBox("Запомнить меня")
        self.checkbox.setObjectName("checkbox")
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        card_layout.addWidget(self.checkbox)
        self.state = False

        card_layout.addSpacing(8)

        # Кнопки действия
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout_2 = QHBoxLayout()
        btn_layout_2.setSpacing(10)

        """self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setObjectName("secondaryButton")
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)
        btn_layout.addWidget(self.btn_cancel)"""

        self.btn_continue = QPushButton("Продолжить")
        self.btn_continue.setObjectName("primaryButton")
        self.btn_continue.clicked.connect(self.on_continue_clicked)
        btn_layout.addWidget(self.btn_continue)

        card_layout.addLayout(btn_layout)

        check_for_acc_label = QLabel("Еще нет аккаунта?")
        check_for_acc_label.setObjectName("fieldLabel")
        card_layout.addWidget(check_for_acc_label)

        self.btn_change = QPushButton("Зарегистрироваться")
        self.btn_change.setObjectName("secondaryButton")
        self.btn_change.clicked.connect(self.on_change_clicked)
        btn_layout_2.addWidget(self.btn_change)

        card_layout.addLayout(btn_layout_2)

        card.setLayout(card_layout)
        layout.addWidget(card, alignment=Qt.AlignHCenter)

        content.setLayout(layout)
        return content

    # Обработчик (запомнить или нет)

    def on_checkbox_changed(self, state):
        checked = state == Qt.Checked
        print(f"[Чекбокс] Запомнить меня: {'включён' if checked else 'выключен'}")
        self.state = state == Qt.Checked
        print(self.state)

    # Обработчики кнопок действия

    def on_continue_clicked(self):
        if self.log_or_reg == "reg":
            print("[Действие] Нажата кнопка: Продолжить # reg")
            print(self.input_name.text())
            print(self.input_email.text())
            print(self.input_psw.text())
            print(self.input_psw_2.text())
            if self.input_psw.text() == self.input_psw_2.text():
                data.state = "reg"
                data.name = self.input_name.text()
                data.email = self.input_email.text()
                data.psw = self.input_psw.text()

        else:
            print("[Действие] Нажата кнопка: Продолжить # log")
            print(self.input_name.text())
            print(self.input_psw.text())
            data.state = "log"
            data.name = self.input_name.text()
            data.psw = self.input_psw.text()
        self.close()  # чтобы далее открыть основное окно

    def on_change_clicked(self):
        clear_layout(self.root)
        if self.log_or_reg == "log":
            print("[Действие] Нажата кнопка: Есть аккаунт # теперь поле рег")
            self.log_or_reg = "reg"

            self.root.addWidget(self.build_content_register(), stretch=1)
            self.setLayout(self.root)
        else:
            print("[Действие] Нажата кнопка: Есть аккаунт # теперь поле лог")
            self.log_or_reg = "log"

            self.root.addWidget(self.build_content_login(), stretch=1)
            self.setLayout(self.root)

    def on_cancel_clicked(self):
        print("[Действие] Нажата кнопка: Отмена")


def return_results(name, psw, rem=False, reg_or_log="log", email=None, psw2=None):
    if reg_or_log == "log":
        return ('log', name, psw)
    return ('reg', name, psw, email, psw == psw2)


"""
TODO: 
сделать экспорт данных после входа / регистрации в main и при этом не хранить переменные с ними
после этого закомментировать принты
"""

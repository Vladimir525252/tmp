import sys
import screeninfo
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QProgressBar,
    QComboBox, QCheckBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from screeninfo import get_monitors

HEIGHT, WIDTH = screeninfo.get_monitors()[0].height, screeninfo.get_monitors()[0].width

print(HEIGHT, WIDTH)


def load_qss(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.dark = False
        self.light_qss = load_qss("modern_light.qss")
        self.dark_qss = load_qss("modern_dark.qss")
        self.setStyleSheet(self.light_qss)
        self.init_ui()

    # UI

    def init_ui(self):
        self.setWindowTitle("EduFlow - <>")
        self.setFixedSize(WIDTH, int(HEIGHT * 0.92))

        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self.build_sidebar())
        root.addWidget(self.build_content(), stretch=1)
        self.setLayout(root)

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(6)

        title = QLabel("EduFlow")
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)
        layout.addSpacing(12)

        self.nav_buttons = []
        for name in ["Главная", "Задания", "Календарь", "Профиль"]:
            btn = QPushButton(name)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(self.on_nav_clicked)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        # первая кнопка активна по умолчанию
        self.nav_buttons[0].setChecked(True)

        layout.addStretch()

        self.theme_btn = QPushButton("🌙 Тёмная тема")
        self.theme_btn.setObjectName("themeButton")
        self.theme_btn.clicked.connect(self.on_toggle_theme)
        layout.addWidget(self.theme_btn)

        sidebar.setLayout(layout)
        return sidebar

    def build_content(self):
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

        # Поле «Имя»
        lbl_name = QLabel("Имя")
        lbl_name.setObjectName("fieldLabel")
        card_layout.addWidget(lbl_name)

        self.input_name = QLineEdit()
        self.input_name.setObjectName("inputField")
        self.input_name.setPlaceholderText("Введите имя")
        self.input_name.returnPressed.connect(self.on_name_enter)
        card_layout.addWidget(self.input_name)

        # Поле "Email"
        lbl_email = QLabel("Email")
        lbl_email.setObjectName("fieldLabel")
        card_layout.addWidget(lbl_email)

        self.input_email = QLineEdit()
        self.input_email.setObjectName("inputField")
        self.input_email.setPlaceholderText("Email")
        self.input_email.returnPressed.connect(self.on_email_enter)
        card_layout.addWidget(self.input_email)

        # Выпадающий список
        lbl_role = QLabel("Роль")
        lbl_role.setObjectName("fieldLabel")
        card_layout.addWidget(lbl_role)

        self.combo_role = QComboBox()
        self.combo_role.setObjectName("comboBox")
        self.combo_role.addItems(["Пользователь", "Разработчик", "Администратор"])
        self.combo_role.currentIndexChanged.connect(self.on_role_changed)
        card_layout.addWidget(self.combo_role)

        card_layout.addSpacing(4)

        # Чекбокс
        self.checkbox = QCheckBox("Запомнить меня")
        self.checkbox.setObjectName("checkbox")
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        card_layout.addWidget(self.checkbox)

        card_layout.addSpacing(8)

        # Кнопки действия
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setObjectName("secondaryButton")
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_continue = QPushButton("Продолжить")
        self.btn_continue.setObjectName("primaryButton")
        self.btn_continue.clicked.connect(self.on_continue_clicked)
        btn_layout.addWidget(self.btn_continue)

        card_layout.addLayout(btn_layout)

        card.setLayout(card_layout)
        layout.addWidget(card, alignment=Qt.AlignHCenter)

        # Прогресс бар
        self.progress = QProgressBar()
        self.progress.setObjectName("progressBar")
        self.progress.setFixedWidth(380)
        self.progress.setValue(60)
        layout.addWidget(self.progress, alignment=Qt.AlignHCenter)

        content.setLayout(layout)
        return content

    # Обработчики навигации

    def on_nav_clicked(self):
        btn = self.sender()
        for button in self.nav_buttons:
            button.setChecked(False)
        btn.setChecked(True)
        print(f"[Навигация] Нажата кнопка: {btn.text()}")

    # Обработчики полей ввода

    def on_name_enter(self):
        print(f"[Ввод] Поле «Имя» → значение: {self.input_name.text()}")

    def on_email_enter(self):
        print(f"[Ввод] Поле «Email» → значение: {self.input_email.text()}")

    # Обработчик выпадающего списка

    def on_role_changed(self, index):
        text = self.combo_role.itemText(index)
        print(f"[Выбор] Роль: {text}")

    # Обработчик чекбокса

    def on_checkbox_changed(self, state):
        checked = state == Qt.Checked
        print(f"[Чекбокс] Запомнить меня: {'включён' if checked else 'выключен'}")

    # Обработчики кнопок действия

    def on_continue_clicked(self):
        print("[Действие] Нажата кнопка: Продолжить")

    def on_cancel_clicked(self):
        print("[Действие] Нажата кнопка: Отмена")

    # Переключение темы

    def on_toggle_theme(self):
        self.dark = not self.dark
        if self.dark:
            self.setStyleSheet(self.dark_qss)
            self.theme_btn.setText("☀️ Светлая тема")
            print("[Тема] Переключена на тёмную тему")
        else:
            self.setStyleSheet(self.light_qss)
            self.theme_btn.setText("🌙 Тёмная тема")
            print("[Тема] Переключена на светлую тему")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

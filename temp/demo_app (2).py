import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QCheckBox, QProgressBar,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt


def load_qss(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class DemoApp(QWidget):
    def __init__(self, user_name):
        super().__init__()
        self.setWindowTitle("EduFlow - <>")
        self.resize(720, 480)
        self._dark = False

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Сайдбар ──
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(16, 20, 16, 20)
        sb_layout.setSpacing(6)

        title = QLabel("EduFlow")
        title.setObjectName("sidebarTitle")
        sb_layout.addWidget(title)
        sb_layout.addSpacing(12)

        self.nav_buttons = []
        nav_items = ["Главная", "Профиль", "Настройки", "О приложении"]
        for name in nav_items:
            btn = QPushButton(name)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, b=btn: self.on_nav_clicked(b))
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        self.nav_buttons[0].setChecked(True)

        sb_layout.addStretch()

        self.theme_btn = QPushButton("🌙 Тёмная тема")
        self.theme_btn.setObjectName("themeButton")
        self.theme_btn.clicked.connect(self.toggle_theme)
        sb_layout.addWidget(self.theme_btn)

        root.addWidget(sidebar)

        # ── Контент ──
        content = QWidget()
        content.setObjectName("content")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 28, 28, 28)
        cl.setSpacing(18)

        # Карточка
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(14)

        card_title = QLabel(f"Привет, {user_name}!")
        card_title.setObjectName("cardTitle")
        card_layout.addWidget(card_title)

        # Поле «Имя»
        name_label = QLabel("Имя")
        name_label.setObjectName("fieldLabel")
        card_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("inputField")
        self.name_input.setPlaceholderText("Введите имя")
        self.name_input.returnPressed.connect(
            lambda: self.on_input_enter(self.name_input, "Имя")
        )
        card_layout.addWidget(self.name_input)

        # Поле «Email»
        email_label = QLabel("Email")
        email_label.setObjectName("fieldLabel")
        card_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setObjectName("inputField")
        self.email_input.setPlaceholderText("example@yandex.ru")
        self.email_input.returnPressed.connect(
            lambda: self.on_input_enter(self.email_input, "Email")
        )
        card_layout.addWidget(self.email_input)

        # Выпадающий список
        role_label = QLabel("Роль")
        role_label.setObjectName("fieldLabel")
        card_layout.addWidget(role_label)

        self.role_combo = QComboBox()
        self.role_combo.setObjectName("comboBox")
        self.role_combo.addItems(["Пользователь", "Редактор", "Администратор"])
        card_layout.addWidget(self.role_combo)

        # Чекбокс
        self.remember_check = QCheckBox("Запомнить меня")
        self.remember_check.setObjectName("checkBox")
        card_layout.addWidget(self.remember_check)

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(
            lambda: self.on_action_button("Отмена")
        )
        btn_row.addWidget(cancel_btn)

        ok_btn = QPushButton("Продолжить")
        ok_btn.setObjectName("primaryButton")
        ok_btn.clicked.connect(
            lambda: self.on_action_button("Продолжить")
        )
        btn_row.addWidget(ok_btn)
        card_layout.addLayout(btn_row)

        cl.addWidget(card)

        # Прогресс-бар
        progress_label = QLabel("Загрузка данных…")
        progress_label.setObjectName("fieldLabel")
        cl.addWidget(progress_label)

        self.progress = QProgressBar()
        self.progress.setObjectName("progressBar")
        self.progress.setValue(65)
        self.progress.setTextVisible(False)
        cl.addWidget(self.progress)

        cl.addStretch()
        root.addWidget(content)

        # Загружаем светлую тему по умолчанию
        self.setStyleSheet(load_qss("modern_light.qss"))

    # ── Обработчики кнопок навигации ──
    def on_nav_clicked(self, btn):
        for b in self.nav_buttons:
            b.setChecked(False)
        btn.setChecked(True)
        print(f"[Навигация] Нажата кнопка: {btn.text()}")

    # ── Обработчик Enter в полях ввода ──
    def on_input_enter(self, field, field_name):
        print(f"[Ввод] Поле «{field_name}» → значение: {field.text()}")

    # ── Обработчик кнопок действия ──
    def on_action_button(self, name):
        print(f"[Действие] Нажата кнопка: {name}")

    # ── Переключение темы ──
    def toggle_theme(self):
        self._dark = not self._dark
        if self._dark:
            self.setStyleSheet(load_qss("modern_dark.qss"))
            self.theme_btn.setText("☀️ Светлая тема")
            print("[Тема] Переключена на тёмную тему")
        else:
            self.setStyleSheet(load_qss("modern_light.qss"))
            self.theme_btn.setText("🌙 Тёмная тема")
            print("[Тема] Переключена на светлую тему")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DemoApp("Владимир")
    win.show()
    sys.exit(app.exec_())

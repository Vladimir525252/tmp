#!/usr/bin/env python3
"""Демонстрация современного интерфейса на PyQt5.

Перед запуском убедитесь, что рядом лежат файлы:
  modern_light.qss
  modern_dark.qss
"""

import sys

import screeninfo
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox, QProgressBar,
    QComboBox, QFrame, QTextEdit, QButtonGroup, QSizePolicy
)
from screeninfo import get_monitors
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont
HEIGHT, WIDTH = screeninfo.get_monitors()[0].height, screeninfo.get_monitors()[0].width
# print(HEIGHT, WIDTH)


# Анимированная кнопка с эффектом hover
class HoverButton(QPushButton):
    """Кнопка с плавной анимацией при наведении (через QSS :hover + доп. opacity)."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        # можно добавить анимацию QSize, но QSS :hover уже даёт хороший эффект


# Главное окно
class MainWindow(QMainWindow):
    def __init__(self, name):
        super().__init__()
        self.setWindowTitle("EduFlow - ")
        self.resize(WIDTH, HEIGHT - 67)

        central = QWidget()
        self.setCentralWidget(central)

        self.name = name

        # Главный layout: сайдбар + контент
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Сайдбар
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(4)

        title = QLabel("EduFlow")
        title.setObjectName("sidebar-title")
        sb_layout.addWidget(title)
        sb_layout.addSpacing(8)

        # Навигация
        nav_group = QButtonGroup(self)
        nav_group.setExclusive(True)
        for text in ["Главная", "Задания", "Календарь", "Профиль"]:
            btn = HoverButton(text)
            btn.setObjectName("nav-btn")
            btn.setCheckable(True)
            nav_group.addButton(btn)
            sb_layout.addWidget(btn)
        # Выделяем первый
        nav_group.buttons()[0].setChecked(True)

        sb_layout.addStretch()

        # Кнопка смены темы внизу сайдбара
        self.theme_btn = QPushButton("🌙 Тёмная тема")
        self.theme_btn.setObjectName("secondary")
        self.theme_btn.clicked.connect(self.toggle_theme)
        sb_layout.addWidget(self.theme_btn)

        root.addWidget(sidebar)

        # Контент
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(32, 32, 32, 32)
        cl.setSpacing(20)

        # Заголовок
        header = QLabel(f"Привет, {self.name}!")
        header.setObjectName("header")
        cl.addWidget(header)

        sub = QLabel("Это пример современного интерфейса на PyQt5 с плоским дизайном, "
                     "скруглёнными углами и мягкими цветами.")
        sub.setObjectName("subheader")
        sub.setWordWrap(True)
        cl.addWidget(sub)

        # Карточка с формой
        card = QFrame()
        card.setObjectName("card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(24, 24, 24, 24)
        card_lay.setSpacing(14)

        card_lay.addWidget(QLabel("Форма ввода"))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя...")
        card_lay.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        card_lay.addWidget(self.email_input)

        # Row: чекбокс + комбобокс
        row = QHBoxLayout()
        row.setSpacing(12)
        self.remember = QCheckBox("Запомнить меня")
        row.addWidget(self.remember)

        combo = QComboBox()
        combo.addItems(["Россия", "Беларусь", "Казахстан"])
        row.addWidget(combo)
        card_lay.addLayout(row)

        # Кнопки
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("secondary")
        btn_row.addWidget(cancel_btn)
        ok_btn = QPushButton("Сохранить")
        btn_row.addWidget(ok_btn)
        card_lay.addLayout(btn_row)

        cl.addWidget(card)

        # Прогресс-бар
        pb_label = QLabel("Прогресс загрузки:")
        cl.addWidget(pb_label)
        self.progress = QProgressBar()
        self.progress.setValue(68)
        cl.addWidget(self.progress)

        # Текстовая область
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Здесь можно писать заметки...")
        self.text_area.setMaximumHeight(100)
        cl.addWidget(self.text_area)

        cl.addStretch()

        root.addWidget(content, 1)

        # Тема
        self.dark_mode = False
        self.apply_theme("modern_light.qss")

    # Смена темы
    def apply_theme(self, qss_file):
        try:
            with open(qss_file, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Файл {qss_file} не найден!")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.theme_btn.setText("☀ Светлая тема")
            self.apply_theme("modern_dark.qss")
        else:
            self.theme_btn.setText("🌙 Тёмная тема")
            self.apply_theme("modern_light.qss")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # базовый стиль, поверх которого работает QSS
    win = MainWindow('Владимир')
    win.show()
    sys.exit(app.exec_())

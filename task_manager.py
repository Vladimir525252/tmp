# класс отвечает за отображание, добавление, изменение и удаление задач
import sys
import json
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QListWidget, QLineEdit, QPushButton,
                             QComboBox, QLabel, QMessageBox, QSplitter, QTabWidget,
                             QDateTimeEdit, QSystemTrayIcon, QMenu, QAction, QDialog)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# pyinstaller --onefile --noconsole --icon=C:\Users\User\PycharmProjects\pythonProject2\icon.ico test.py
class Task:
    """
    Класс, представляющий отдельную задачу.
    Содержит все свойства задачи: название, приоритет, категорию, статус выполнения и даты.
    """

    def __init__(self, title, priority="Средний", category="Работа", completed=False,
                 notification_datetime=None, notification_sent=False):
        self.title = title
        self.priority = priority
        self.category = category
        self.completed = completed
        self.created_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        self.completed_date = None
        self.notification_datetime = notification_datetime
        self.notification_sent = notification_sent

    def to_dict(self):
        """Преобразует объект задачи в словарь для сериализации в JSON.
        Возвращает: словарь с данными задачи"""
        return {
            'title': self.title,
            'priority': self.priority,
            'category': self.category,
            'completed': self.completed,
            'created_date': self.created_date,
            'completed_date': self.completed_date,
            'notification_datetime': self.notification_datetime,
            'notification_sent': self.notification_sent
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект задачи из словаря (при загрузке из JSON).
        Args:
            data: словарь с данными задачи
        Возвращает объект Task"""
        task = cls(data['title'], data['priority'], data['category'], data['completed'])
        task.created_date = data['created_date']
        task.completed_date = data['completed_date']
        task.notification_datetime = data.get('notification_datetime')
        task.notification_sent = data.get('notification_sent', False)
        return task


class NotificationDialog(QDialog):
    """Диалоговое окно для уведомления о задаче.
    Всегда поверх всех окон, без кнопки свернуть."""

    def __init__(self, task_title, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Напоминание о задаче")
        self.setModal(True)
        # Убираем иконку в панели задач и делаем ToolTip
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.CustomizeWindowHint |
                            Qt.WindowTitleHint | Qt.Tool)
        self.setFixedSize(400, 200)

        # Убираем кнопку свернуть
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint)

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<h2>⏰ Время выполнить задачу!</h2>"))
        layout.addWidget(QLabel(f"<b style='font-size: 14px;'>{task_title}</b>"))

        # Добавляем отступ
        layout.addSpacing(20)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setFixedHeight(40)
        btn_layout.addWidget(ok_btn)

        snooze_btn = QPushButton("Отложить (5 мин)")
        snooze_btn.clicked.connect(self.snooze)
        snooze_btn.setFixedHeight(40)
        btn_layout.addWidget(snooze_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Активируем окно и поднимаем его поверх всех
        self.activateWindow()
        self.raise_()
        # Позиционирование в правом нижнем углу экрана
        screen_geometry = QApplication.desktop().screenGeometry()
        x = screen_geometry.width() - self.width() - 19  # 20px от правого края
        y = screen_geometry.height() - self.height() - 80  # 60px от нижнего края (чтобы не мешать панели задач)
        self.move(x, y)

    def snooze(self):
        # Отложить уведомление на 5 минут
        self.done(1)  # Возвращаем код 1 для отложенного уведомления

    def showEvent(self, event):
        # Переопределяем показ окна чтобы гарантировать позиционирование поверх всех
        super().showEvent(event)
        self.activateWindow()
        self.raise_()


class MplCanvas(FigureCanvas):
    """Кастомный виджет для отображения графиков matplotlib в PyQt.
    Наследуется от FigureCanvas для интеграции с Qt."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)


class AnalyticsTab(QWidget):
    """Вкладка с аналитикой и графиками.
    Отображает статистику по задачам в виде диаграмм."""

    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks  # Ссылка на список задач из главного окна
        self.initUI()
        self.update_charts()

    def initUI(self):
        # Инициализация пользовательского интерфейса вкладки аналитики
        layout = QVBoxLayout()

        # График выполненных задач по дням
        self.canvas1 = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(QLabel("Выполненные задачи по дням:"))
        layout.addWidget(self.canvas1)

        # График распределения по приоритетам
        self.canvas2 = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(QLabel("Распределение по приоритетам:"))
        layout.addWidget(self.canvas2)

        # График по категориям
        self.canvas3 = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(QLabel("Распределение по категориям:"))
        layout.addWidget(self.canvas3)

        self.setLayout(layout)

    def update_charts(self):
        # Обновление всех графиков аналитики
        self.update_daily_completion_chart()
        self.update_priority_chart()
        self.update_category_chart()

    def update_daily_completion_chart(self):
        # Обновление графика выполненных задач по дням
        # Фильтруем только выполненные задачи
        completed_tasks = [task for task in self.tasks if task.completed]
        dates = {}  # Словарь для подсчета задач по датам

        # Считаем количество выполненных задач для каждой даты
        for task in completed_tasks:
            date = task.completed_date[:10] if task.completed_date else datetime.datetime.now().strftime("%d-%m-%Y")
            dates[date] = dates.get(date, 0) + 1

        # Создаем график только если есть данные
        if dates:
            self.canvas1.fig.clear()
            ax = self.canvas1.fig.add_subplot(111)
            ax.bar(dates.keys(), dates.values())
            ax.set_xticklabels(dates.keys(), rotation=0)
            ax.set_ylabel('Количество задач')
            self.canvas1.draw()

    def update_priority_chart(self):
        # Обновление круговой диаграммы распределения задач по приоритетам
        priorities = {}
        # Считаем количество задач для каждого приоритета
        for task in self.tasks:
            priorities[task.priority] = priorities.get(task.priority, 0) + 1

        # Создаем круговую диаграмму
        self.canvas2.fig.clear()
        ax = self.canvas2.fig.add_subplot(111)
        ax.pie(priorities.values(), labels=priorities.keys(), autopct='%1.1f%%')
        self.canvas2.draw()

    def update_category_chart(self):
        # Обновление графика распределения задач по категориям
        categories = {}
        # Считаем количество задач для каждой категории
        for task in self.tasks:
            categories[task.category] = categories.get(task.category, 0) + 1

        # Создаем столбчатую диаграмму
        self.canvas3.fig.clear()
        ax = self.canvas3.fig.add_subplot(111)
        ax.bar(categories.keys(), categories.values())
        ax.set_xticklabels(categories.keys(), rotation=0)
        ax.set_ylabel('Количество задач')
        self.canvas3.draw()


class TaskManager(QMainWindow):
    """Главное окно приложения - менеджер задач.
    Содержит интерфейс для управления задачами и отображения аналитики."""

    def __init__(self):
        super().__init__()
        self.tasks = []  # Список всех задач
        self.notification_timer = QTimer()  # Таймер для проверки уведомлений
        self.notification_timer.timeout.connect(self.check_notifications)
        self.notification_timer.start(10000)  # Проверка каждые 10 секунд

        self.tray_icon = None
        self.setup_tray_icon()

        self.load_tasks()  # Загрузка задач из файла при запуске
        self.initUI()  # Инициализация интерфейса

    def setup_tray_icon(self):
        # Настройка иконки в системном трее
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon('icon.ico'))

            tray_menu = QMenu()

            show_action = QAction("Показать", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            quit_action = QAction("Выход", self)
            quit_action.triggered.connect(self.quit_application)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            self.tray_icon.show()

    def tray_icon_activated(self, reason):
        # Обработка активации иконки в трее
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()

    def quit_application(self):
        # Корректный выход из приложения
        self.save_tasks()
        QApplication.quit()

    def initUI(self):
        # Инициализация пользовательского интерфейса главного окна
        self.setWindowTitle('TaskAnalyst - Умный менеджер задач v4.1')
        self.setGeometry(100, 100, 1000, 700)  # Позиция и размер окна
        icon = QIcon('icon.ico')
        self.setWindowIcon(icon)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Левая панель - управление задачами
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # Поле ввода новой задачи
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Введите новую задачу...")
        self.task_input.returnPressed.connect(self.add_task)  # Добавление по Enter
        left_layout.addWidget(self.task_input)

        # Панель параметров задачи (приоритет и категория)
        params_layout = QHBoxLayout()
        params_layout.addWidget(QLabel("Приоритет:"))

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Высокий", "Средний", "Низкий"])
        params_layout.addWidget(self.priority_combo)

        params_layout.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Работа", "Учеба", "Личное", "Здоровье", "Другое"])
        params_layout.addWidget(self.category_combo)

        left_layout.addLayout(params_layout)

        # Панель для установки уведомления
        notification_layout = QHBoxLayout()
        notification_layout.addWidget(QLabel("Уведомление:"))

        self.notification_datetime = QDateTimeEdit()
        self.notification_datetime.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # +1 час по умолчанию
        self.notification_datetime.setCalendarPopup(True)
        self.notification_datetime.setDisplayFormat("dd-MM-yyyy HH:mm")
        notification_layout.addWidget(self.notification_datetime)

        self.notification_checkbox = QPushButton("Добавить напоминание")
        self.notification_checkbox.setCheckable(True)
        self.notification_checkbox.setChecked(False)
        self.notification_checkbox.clicked.connect(self.toggle_notification_widget)
        notification_layout.addWidget(self.notification_checkbox)

        left_layout.addLayout(notification_layout)

        # Кнопка добавления задачи
        add_btn = QPushButton("Добавить задачу")
        add_btn.clicked.connect(self.add_task)
        left_layout.addWidget(add_btn)

        # Список задач
        self.task_list = QListWidget()
        self.task_list.itemDoubleClicked.connect(self.toggle_task)  # Двойной клик - изменение статуса
        left_layout.addWidget(self.task_list)

        # Кнопки управления задачами
        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_task)
        btn_layout.addWidget(delete_btn)

        clear_btn = QPushButton("Очистить выполненные")
        clear_btn.clicked.connect(self.clear_completed)
        btn_layout.addWidget(clear_btn)

        notification_btn = QPushButton("Управление уведомлениями")
        notification_btn.clicked.connect(self.manage_notifications)
        btn_layout.addWidget(notification_btn)

        left_layout.addLayout(btn_layout)

        left_panel.setLayout(left_layout)

        # Правая панель - аналитика (вкладки)
        self.tabs = QTabWidget()

        # Создаем вкладку аналитики и передаем ей список задач
        self.analytics_tab = AnalyticsTab(self.tasks)
        self.tabs.addTab(self.analytics_tab, "Аналитика")

        # Разделитель для изменения размера панелей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.tabs)
        splitter.setSizes([400, 600])  # Начальные размеры панелей

        main_layout.addWidget(splitter)

        self.update_task_list()  # Первоначальное обновление списка задач

    def toggle_notification_widget(self):
        # Включение/выключения виджета уведомления
        self.notification_datetime.setEnabled(self.notification_checkbox.isChecked())

    def add_task(self):
        # Добавление новой задачи
        title = self.task_input.text().strip()
        if title:  # Проверяем, что поле не пустое
            priority = self.priority_combo.currentText()
            category = self.category_combo.currentText()

            # Получаем дату уведомления если установлен флажок
            notification_datetime = None
            if self.notification_checkbox.isChecked():
                # Преобразуем QDateTime в наш строковый формат
                qdatetime = self.notification_datetime.dateTime()
                notification_datetime = qdatetime.toString("dd-MM-yyyy HH:mm")

                # Проверяем, что дата не в прошлом
                selected_dt = qdatetime.toPyDateTime()
                if selected_dt < datetime.datetime.now():
                    QMessageBox.warning(self, "Предупреждение",
                                        "Выбрана дата в прошлом! Уведомление может сработать сразу.")

            task = Task(title, priority, category, notification_datetime=notification_datetime)
            self.tasks.append(task)
            self.task_input.clear()  # Очищаем поле ввода
            self.notification_checkbox.setChecked(False)
            self.notification_datetime.setEnabled(False)
            self.update_task_list()
            self.save_tasks()  # Сохраняем изменения в файл

    def toggle_task(self, item):
        # Изменение статуса выполнения задачи (выполнена/не выполнена)
        index = self.task_list.row(item)
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            task.completed = not task.completed  # Инвертируем статус
            # Устанавливаем дату выполнения если задача завершена
            task.completed_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M") if task.completed else None
            self.update_task_list()
            self.save_tasks()
            self.analytics_tab.update_charts()  # Обновляем графики

    def delete_task(self):
        # Удаление выбранной задачи
        current_row = self.task_list.currentRow()
        if current_row >= 0:
            self.tasks.pop(current_row)
            self.update_task_list()
            self.save_tasks()
            self.analytics_tab.update_charts()

    def clear_completed(self):
        # Удаление всех выполненных задач
        self.tasks = [task for task in self.tasks if not task.completed]
        self.update_task_list()
        self.save_tasks()
        self.analytics_tab.update_charts()

    def manage_notifications(self):
        # Управление уведомлениями для выбранной задачи
        current_row = self.task_list.currentRow()
        if current_row >= 0:
            task = self.tasks[current_row]

            # Диалог для управления уведомлением
            dialog = QDialog(self)
            dialog.setWindowTitle("Управление уведомлением")
            dialog.resize(300, 200)

            layout = QVBoxLayout()

            layout.addWidget(QLabel(f"Задача: {task.title}"))

            notification_layout = QVBoxLayout()
            notification_layout.addWidget(QLabel("Дата и время уведомления:"))

            datetime_edit = QDateTimeEdit()
            if task.notification_datetime:
                datetime_edit.setDateTime(QDateTime.fromString(task.notification_datetime, "dd-MM-yyyy HH:mm"))
            else:
                datetime_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))
            datetime_edit.setCalendarPopup(True)
            datetime_edit.setDisplayFormat("dd-MM-yyyy HH:mm")
            notification_layout.addWidget(datetime_edit)

            layout.addLayout(notification_layout)

            btn_layout = QHBoxLayout()
            save_btn = QPushButton("Сохранить")
            save_btn.clicked.connect(lambda: self.save_notification(task, datetime_edit, dialog))
            btn_layout.addWidget(save_btn)

            remove_btn = QPushButton("Удалить уведомление")
            remove_btn.clicked.connect(lambda: self.remove_notification(task, dialog))
            btn_layout.addWidget(remove_btn)

            cancel_btn = QPushButton("Отмена")
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)

            layout.addLayout(btn_layout)
            dialog.setLayout(layout)
            dialog.exec_()

    def save_notification(self, task, datetime_edit, dialog):
        # Сохранение уведомления для задачи
        task.notification_datetime = datetime_edit.dateTime().toString("dd-MM-yyyy HH:mm")
        task.notification_sent = False
        self.update_task_list()
        self.save_tasks()
        dialog.accept()

    def remove_notification(self, task, dialog):
        # Удаление уведомления для задачи
        task.notification_datetime = None
        task.notification_sent = False
        self.update_task_list()
        self.save_tasks()
        dialog.accept()

    def update_task_list(self):
        # Обновление отображения списка задач
        self.task_list.clear()
        for task in self.tasks:
            # Символы для отображения статуса: ✓ - выполнено, □ - не выполнено
            status = "✓ " if task.completed else "□ "
            notification_indicator = " 🔔" if task.notification_datetime and not task.completed else ""
            item_text = f"{status}{task.title} [{task.priority}] - {task.category}{notification_indicator}"
            self.task_list.addItem(item_text)

    def check_notifications(self):
        # Проверка уведомлений для всех задач
        current_datetime = datetime.datetime.now()

        for task in self.tasks:
            if (task.notification_datetime and
                    not task.notification_sent and
                    not task.completed):

                # Преобразуем строку в datetime для корректного сравнения
                try:
                    notification_dt = datetime.datetime.strptime(task.notification_datetime, "%d-%m-%Y %H:%M")

                    # Сравниваем как datetime объекты
                    if notification_dt <= current_datetime:
                        # Показываем уведомление
                        self.show_notification(task)
                        task.notification_sent = True
                        self.save_tasks()

                except ValueError as e:
                    print(f"Ошибка в формате даты у задачи '{task.title}': {e}")

    def show_notification(self, task):
        # Показ уведомления о задаче
        # Создаем и показываем модальное окно уведомления
        dialog = NotificationDialog(task.title)
        result = dialog.exec_()

        if result == 1:  # Отложить на 5 минут
            # Обновляем время уведомления на +5 минут, используя datetime
            current_dt = datetime.datetime.now()
            new_dt = current_dt + datetime.timedelta(minutes=5)
            task.notification_datetime = new_dt.strftime("%d-%m-%Y %H:%M")
            task.notification_sent = False
            self.save_tasks()

        # Также показываем уведомление в системном трее
        if self.tray_icon:
            self.tray_icon.showMessage(
                "Напоминание о задаче",
                f"Время выполнить: {task.title}",
                QSystemTrayIcon.Information,
                5000  # Показывать 5 секунд
            )

    def save_tasks(self):
        # Сохранение задач в JSON файл
        data = [task.to_dict() for task in self.tasks]
        with open('tasks.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        # Загрузка задач из JSON файла
        try:
            with open('tasks.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(item) for item in data]
        except FileNotFoundError:
            # Если файл не найден, создаем пустой список задач
            self.tasks = []

    def closeEvent(self, event):
        """Обработчик события закрытия окна.
        Автоматически сохраняет задачи перед выходом."""
        # Не закрываем приложение, а скрываем в трей
        if self.tray_icon and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            if self.tray_icon:
                self.tray_icon.showMessage(
                    "TaskAnalyst",
                    "Приложение продолжает работать в фоновом режиме",
                    QSystemTrayIcon.Information,
                    2000
                )
        else:
            self.save_tasks()
            event.accept()


def main():
    """Главная функция приложения.
    Создает экземпляр QApplication и главного окна, запускает цикл событий."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Устанавливаем стиль интерфейса
    app.setQuitOnLastWindowClosed(False)  # Не завершать приложение при закрытии окна
    # app.setStyleSheet("QPushButton { border: 2px solid grey; }")
    with open("modern_light.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    manager = TaskManager()
    manager.show()

    sys.exit(app.exec())  # Запуск цикла событий


if __name__ == '__main__':
    main()

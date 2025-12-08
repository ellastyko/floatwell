from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from .styles import *
from qt.widgets.components.inputs import create_labeled_combobox
from qt.widgets.components.buttons import PushButton
from qt.controllers import parser
from qt.signals import data_bus

class ProxiesPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setStyleSheet("""
            border-radius: 5px;
            background-color: #303030;
            color: white;
        """)

        # Создаем заголовок
        self.label_title = QLabel("Proxies")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            background-color: #212121; 
            padding: 5px;
            margin-bottom: 10px;
        """)

        layout.addWidget(self.label_title)

        layout.addStretch()

class ControlPanel(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setStyleSheet("""
            border-radius: 5px;
            background-color: #303030;
            color: white;
        """)

        # Создаем заголовок
        self.label_title = QLabel("Controller")
        self.label_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            background-color: #212121; 
            padding: 5px;
            margin-bottom: 10px;
        """)
        self.label_title.setAlignment(Qt.AlignCenter)

        self.run_parsing_btn = PushButton("Run parsing")
        # self.restart_btn = PushButton("Restart")
        self.pause_btn = PushButton("Pause")
        self.run_parsing_btn.clicked.connect(self.on_run)
        # self.restart_btn.clicked.connect(self.on_restart)
        self.pause_btn.clicked.connect(self.on_pause)

        layout.addWidget(self.label_title, 1)
        layout.addStretch(8)
        layout.addWidget(self.run_parsing_btn)
        # layout.addWidget(self.restart_btn)
        layout.addWidget(self.pause_btn)
    
    def on_new_data(self, item_data):
        data_bus.add_items.emit(item_data)
     
    def on_run(self):
        # если слот ещё не подключен — подключаем
        try:
            parser.new_data.disconnect(self.on_new_data)
        except TypeError:
            pass
        parser.new_data.connect(self.on_new_data)

        # кнопки
        self.run_parsing_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        # self.restart_btn.setEnabled(True)

        parser.start()  # запускаем парсер
        
        # self.items_table.update_row(item_data)
    # def on_restart(self):
    #     # отключаем слот, чтобы не обрабатывались старые данные
    #     try:
    #         parser.new_data.disconnect(self.on_new_data)
    #     except TypeError:
    #         pass

    #     # после остановки воркера снова запустить
    #     def restart_after_stop():
    #         parser.stopped.disconnect(restart_after_stop)
    #         parser.new_data.connect(self.on_new_data)
    #         parser.start()
    #         self.run_parsing_btn.setEnabled(False)
    #         self.pause_btn.setEnabled(True)
    #         self.restart_btn.setEnabled(True)

    #     parser.stopped.connect(restart_after_stop)
    #     parser.stop()

    def on_pause(self):
        # после остановки воркера включаем кнопки
        def pause_after_stop():
            parser.stopped.disconnect(pause_after_stop)
            self.run_parsing_btn.setEnabled(True)
            # self.restart_btn.setEnabled(True)

        parser.stopped.connect(pause_after_stop)
        parser.stop()
        self.pause_btn.setEnabled(False)


        
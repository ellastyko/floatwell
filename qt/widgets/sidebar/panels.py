from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from .styles import *
from qt.widgets.components.inputs import create_labeled_combobox
from qt.widgets.components.buttons import PushButton
from qt.controllers import parser
from qt.widgets.components.bars import LoadingBar
from utils.helpers import files_dict
from configurator import config
from core.source import source_manager
from core.settings import settings_manager
from utils.helpers import resource_path, load_json_resource

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
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setStyleSheet("""
            border-radius: 5px;
            background-color: #303030;
            color: white;
        """)
        
        currency_select = self.setup_currency_select()
        source_select = self.setup_source_select()

        self.layout.addWidget(currency_select)
        self.layout.addWidget(source_select)
        self.layout.addStretch(8)

        self.setup_buttons()

    
    def setup_buttons(self):
        self.run_btn = PushButton("Run parsing")
        self.pause_btn = PushButton("Pause")

        self.run_btn.clicked.connect(self.on_run)
        self.pause_btn.clicked.connect(self.on_pause)
        parser.stopped.connect(self.on_worker_finished)

        self.layout.addWidget(self.run_btn)
        self.layout.addWidget(self.pause_btn)
    
    # Currency
    def setup_currency_select(self):
        container, combo = create_labeled_combobox("Currency:")

        currencies = load_json_resource(config['resources']['currencies'])

        saved_currency = settings_manager.get('currency') # сохраненный source name

        for currency in currencies:
            combo.addItem(currency['name'], currency)
        
        # Если есть сохранённый source — выставляем его
        if saved_currency:
            index = combo.findText(saved_currency['name'])
            if index != -1:
                combo.setCurrentIndex(index)

        combo.currentIndexChanged.connect(self.currency_changed)

        return container

    def currency_changed(self, index):
        combo = self.sender()
        data = combo.itemData(index)   

        # Обновляем сохранённый выбор
        settings_manager.set('currency', data)
    
    # Source
    def setup_source_select(self):
        container, combo = create_labeled_combobox("Source:")

        sources = files_dict(resource_path(config['sources']['dir']))

        saved_source = settings_manager.get('source') # сохраненный source name

        for name, path in sources.items():
            combo.addItem(name, path)
        
        # Если есть сохранённый source — выставляем его
        if saved_source:
            index = combo.findText(saved_source)
            if index != -1:
                combo.setCurrentIndex(index)
                source_manager.set_source(name, path)

        combo.currentIndexChanged.connect(self.source_changed)

        return container
    
    def source_changed(self, index):
        combo = self.sender()
        name = combo.currentText()     # имя берём из текста
        path = combo.itemData(index)   # путь берём из itemData

        # Обновляем сохранённый выбор
        settings_manager.set('source', name)

        source_manager.set_source(name, path)
    
    # Control buttons
    def on_worker_finished(self):
        self.run_btn.setEnabled(True) 
        self.pause_btn.setDisabled(True)

    def on_run(self):
        self.run_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)

        parser.start()  # запускаем парсер
        
    def on_pause(self):        
        parser.stop()


        
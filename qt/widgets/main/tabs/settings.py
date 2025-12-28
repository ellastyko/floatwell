from PyQt5.QtWidgets import (QWidget, QVBoxLayout)
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from qt.style import StyleManager
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from utils.helpers import load_json_resource
from qt.widgets.components.inputs import create_labeled_combobox
from qt.widgets.components.buttons import PushButton
from core.settings import settings_manager
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QGroupBox
from configurator import config
from qt.widgets.components.inputs import TelegramTokenInput
from utils.helpers import files_dict
from configurator import config
from core.source.manager import source_manager
from core.settings import settings_manager
from utils.helpers import resource_path, load_json_resource

class SettingsTabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        self.setObjectName("SettingsTab")
        self.setStyleSheet("""
            #SettingsTab {
                background-color: #1e1e1e;
                color: #f8faff;
            }
        """)

        layout.addWidget(GeneralSettingsSection())
        layout.addWidget(TelegramSettingsSection())
        layout.addWidget(AdvancedSettingsSection())
        layout.addStretch()
    
class SettingsSection(QWidget):
    def __init__(self, title: str, description: str | None = None):
        super().__init__()

        self.setObjectName("SettingsSection")
        self.setAttribute(Qt.WA_StyledBackground, True) 

        self.layout = QVBoxLayout(self)  # <- Сохраняем как атрибут
        self.layout.setContentsMargins(14, 12, 14, 14)
        self.layout.setSpacing(10)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("SectionTitle")
        self.layout.addWidget(title_lbl)

        if description:
            desc = QLabel(description)
            desc.setWordWrap(True)
            desc.setObjectName("SectionDescription")
            self.layout.addWidget(desc)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        self.layout.addLayout(self.content_layout)

        self.setStyleSheet("""
            #SettingsSection {
                background-color: #181818;
                border: 1px solid #2f2f2f;
                border-radius: 6px;
            }

            #SectionTitle {
                background-color: transparent;           
                font-size: 13px;
                font-weight: 600;
                color: #f0f0f0;
            }

            #SectionDescription {
                background-color: transparent;
                font-size: 11px;
                color: #9a9a9a;
            }
        """)

        
class GeneralSettingsSection(SettingsSection):
    def __init__(self):
        super().__init__(
            "General",
            "Basic application preferences"
        )
        
        self.layout.addWidget(self._setup_currency_select())
        self.layout.addWidget(self._setup_source_select())

    def _setup_currency_select(self):
        container, self.currency_combo = create_labeled_combobox("Currency")

        currencies = load_json_resource(config['resources']['currencies'])
        saved = settings_manager.get('currency')

        for cur in currencies:
            self.currency_combo.addItem(cur['name'], cur)

        if saved:
            idx = self.currency_combo.findText(saved['name'])
            if idx != -1:
                self.currency_combo.setCurrentIndex(idx)

        self.currency_combo.currentIndexChanged.connect(self.on_currency_changed)
        return container

    def on_currency_changed(self, index):
        data = self.currency_combo.itemData(index)
        settings_manager.set('currency', data)
    
    # Source
    def _setup_source_select(self):
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
                name = combo.itemText(index)
                path = combo.itemData(index)
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


class TelegramSettingsSection(SettingsSection):
    def __init__(self):
        super().__init__(
            "Telegram Notifications (In development)",
            "Receive important events directly in Telegram"
        )

        self.enable_cb = QCheckBox("Enable Telegram notifications")
        self.enable_cb.setAttribute(Qt.WA_StyledBackground, True)
        self.enable_cb.setStyleSheet('background-color: transparent;')
        self.content_layout.addWidget(self.enable_cb)

        # Поле для токена
        self.token_field = TelegramTokenInput()
        self.content_layout.addWidget(self.token_field)

class AdvancedSettingsSection(SettingsSection):
    def __init__(self):
        super().__init__(
            "Advanced (In development)",
            "Danger zone. Incorrect usage may break account synchronization."
        )

        self.setStyleSheet(self.styleSheet() + """
            QWidget#SettingsSection {
                border: 1px solid #5a3a3a;
                background-color: #1b1414;
            }
        """)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        attach = PushButton("Attach maFile")
        remove = PushButton("Remove maFile")

        attach.setFixedWidth(160)
        remove.setFixedWidth(160)

        btn_row.addWidget(attach)
        btn_row.addWidget(remove)
        btn_row.addStretch()

        self.content_layout.addLayout(btn_row)
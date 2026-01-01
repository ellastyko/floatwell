from PyQt5.QtWidgets import QComboBox, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from qt.style import StyleManager
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit
from qt.widgets.components.buttons import PushButton
from core.settings import settings_manager
from PyQt5.QtCore import QObject, pyqtSignal

class ComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setStyleSheet(StyleManager.get_style("QComboBox"))


def create_labeled_combobox(label_text, parent=None):
    container = QWidget(parent)
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    
    # Создаем Label
    label = QLabel(label_text)
    label.setProperty("class", "combo-label")
    label.setStyleSheet(StyleManager.get_style("ComboLabel"))
    
    # Создаем ComboBox
    combo = ComboBox()
    combo.setProperty("class", "with-label")
    
    # Добавляем в контейнер
    layout.addWidget(label)
    layout.addWidget(combo)
    
    return container, combo  # Возвращаем контейнер и комбобокс для доступа


class TelegramTokenInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)

        # Поле ввода токена
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your Telegram bot token")
        self.token_input.setMinimumHeight(28)
        self.token_input.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                color: #f8faff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #5a9fff;
                background-color: #2a2a2a;
            }
            QLineEdit::placeholder {
                color: #7a7a7a;
            }
        """)

        saved_token = settings_manager.get('telegram.BOT_TOKEN')

        if saved_token:
            self.token_input.setText(saved_token)
            
        self.layout.addWidget(self.token_input)

        # Кнопка сохранения
        self.save_button = PushButton("💾")  # Можно поставить иконку дискеты
        self.save_button.setToolTip("Save token")
        self.save_button.setFixedSize(36, 28)

        self.save_button.clicked.connect(self.save_token)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_token(self):
        token = self.token_input.text()
        settings_manager.set('telegram.BOT_TOKEN', str(token))


class ChatIdRow(QWidget):
    removed = pyqtSignal(QWidget)

    def __init__(self, value: str = "", parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Chat ID (e.g. 123456789 or -100...)")
        self.input.setText(value)
        self.input.setMinimumHeight(28)
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #252525;
                color: #f8faff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #5a9fff;
            }
        """)

        remove_btn = PushButton("✕")
        remove_btn.setFixedSize(28, 28)
        remove_btn.clicked.connect(lambda: self.removed.emit(self))

        layout.addWidget(self.input)
        layout.addWidget(remove_btn)

class TelegramChatIdsInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)

        self.rows: list[ChatIdRow] = []

        saved_ids = settings_manager.get('telegram.CHAT_IDS', [])

        for chat_id in saved_ids:
            self.add_row(str(chat_id))

        add_btn = PushButton("➕ Add chat")
        add_btn.clicked.connect(lambda: self.add_row())

        save_btn = PushButton("💾 Save chats")
        save_btn.clicked.connect(self.save)

        self.layout.addWidget(add_btn)
        self.layout.addWidget(save_btn)

    def add_row(self, value: str = ""):
        row = ChatIdRow(value)
        row.removed.connect(self.remove_row)

        self.rows.append(row)
        self.layout.insertWidget(len(self.rows) - 1, row)

    def remove_row(self, row: ChatIdRow):
        self.rows.remove(row)
        row.deleteLater()

    def save(self):
        ids = []

        for row in self.rows:
            value = row.input.text().strip()
            if value:
                try:
                    ids.append(int(value))
                except ValueError:
                    pass  # можно потом подсветить ошибку

        settings_manager.set('telegram.CHAT_IDS', ids)

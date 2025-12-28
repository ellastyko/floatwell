from PyQt5.QtWidgets import QComboBox, QWidget, QHBoxLayout, QLabel
from qt.style import StyleManager
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit
from qt.widgets.components.buttons import PushButton

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
        print(f"Token saved: {token}")
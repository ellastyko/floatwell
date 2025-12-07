from PyQt5.QtWidgets import QComboBox, QWidget, QHBoxLayout, QLabel
from qt.style import StyleManager

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
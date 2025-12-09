from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QHeaderView, QGroupBox,
    QVBoxLayout, QTableWidgetItem, QPushButton
)
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import webbrowser
from qt.style import StyleManager
from PyQt5.QtGui import QColor

class ItemsTableDispatcher(QObject):
    add_rows = pyqtSignal(list)

dispatcher = ItemsTableDispatcher()

class ItemsTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        dispatcher.add_rows.connect(self.add_rows)

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table_widget = QTableWidget(0, 9)
        self.table_widget.setStyleSheet(StyleManager.get_style("QTable"))
        self.table_widget.setHorizontalHeaderLabels(
            ["Name", "Assets", "Float", "Pattern", "Price", "Sync At", "Inspect", "Steam", "Actions"]
        )

        header = self.table_widget.horizontalHeader()

        # Настроим размеры колонок
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Assets
        # header.setMaximumSectionSize(300) 
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Float
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Pattern
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Price
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Sync At
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # Inspect (кнопка)
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Buy (кнопка)
        header.setSectionResizeMode(8, QHeaderView.Fixed)

        self.table_widget.setColumnWidth(5, 120)  # меньше, чем растягиваемые колонки
        # Фиксируем ширину для кнопок и Sync At
        self.table_widget.setColumnWidth(6, 80)
        self.table_widget.setColumnWidth(7, 80)
        self.table_widget.setColumnWidth(8, 80)

        table_box = QGroupBox(" Listings ")
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table_widget)
        table_box.setLayout(table_layout)
        layout.addWidget(table_box)
    
    def add_rows(self, items):
        for item in items:
            self.table_widget.insertRow(0)
            name_item = QTableWidgetItem(item["name_col"])
            name_item.setData(Qt.UserRole, item["listing_id_col"])  # храним уникальный ID
            self.table_widget.setItem(0, 0, name_item)
            self.table_widget.setItem(0, 1, QTableWidgetItem(str(item["assets_col"])))
            self.table_widget.setItem(0, 2, QTableWidgetItem(str(item["float_col"])))
            self.table_widget.setItem(0, 3, QTableWidgetItem(str(item["pattern_col"])))
            self.table_widget.setItem(0, 4, QTableWidgetItem(str(item["converted_price_col"])))
            self.table_widget.setItem(0, 5, QTableWidgetItem(str(item["sync_at_col"])))

            inspect_button = QPushButton("Inspect")
            inspect_button.setCursor(Qt.PointingHandCursor)
            inspect_button.clicked.connect(lambda _, url=item["inspect_link_col"]: webbrowser.open(url))
            self.table_widget.setCellWidget(0, 6, inspect_button)

            buy_button = QPushButton("Buy")
            buy_button.setCursor(Qt.PointingHandCursor)
            buy_button.clicked.connect(lambda _, url=item["buy_url_col"]: webbrowser.open(url))
            self.table_widget.setCellWidget(0, 7, buy_button)

             # Remove — ★ new ★
            remove_button = QPushButton("Remove")
            remove_button.setCursor(Qt.PointingHandCursor)
            remove_button.clicked.connect(
                lambda _, btn=remove_button: self.remove_row(btn)
            )
            self.table_widget.setCellWidget(0, 8, remove_button)
            
            # ---- Подсветка строки, если нужно ----
            # if item['is_highlighted']:
            #     for col in range(self.table_widget.columnCount()):
            #         cell_item = self.table_widget.item(row, col)
            #         if cell_item:
            #             cell_item.setBackground(QColor("#25A550"))  # светло-жёлтая подсветка
            #             cell_item.setForeground(QColor("#000000"))  # черный текст
        
    def remove_row(self, button):
        index = self.table_widget.indexAt(button.pos())
        row = index.row()
        if row >= 0:
            self.table_widget.removeRow(row)

    def reset_table(self):
        self.table_widget.setRowCount(0)

from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QHeaderView, QGroupBox,
    QVBoxLayout, QTableWidgetItem, QPushButton
)
from PyQt5.QtCore import Qt
import webbrowser
from qt.signals import data_bus
from qt.style import StyleManager
from PyQt5.QtGui import QColor

class ItemsTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

        self.records = []

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 6 колонок: Name, Assets, Float, Pattern, Price, Inspect, Buy
        self.table_widget = QTableWidget(0, 8)
        self.table_widget.setStyleSheet(StyleManager.get_style("QTable"))

        self.table_widget.setHorizontalHeaderLabels(
            ["Name", "Assets", "Float", "Pattern", "Price", "Inspect", "Buy", "Sync At"]
        )
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table_box = QGroupBox(" Listings ")
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table_widget)
        table_box.setLayout(table_layout)

        layout.addWidget(table_box)

        data_bus.update_items.connect(self.update_table)
        data_bus.add_items.connect(self.add_or_update_rows)
    
    def add_or_update_rows(self, items):
        for item in items:
            # ищем строку с таким же listing_id
            found = False
            for row in range(self.table_widget.rowCount()):
                if self.table_widget.item(row, 0) and self.table_widget.item(row, 0).data(Qt.UserRole) == item["listing_id"]:
                    # обновляем значения
                    self.table_widget.item(row, 1).setText(str(item["assets"]))
                    self.table_widget.item(row, 2).setText(str(item["float"]))
                    self.table_widget.item(row, 3).setText(str(item["pattern"]))
                    self.table_widget.item(row, 4).setText(str(item["converted_price"]))
                    self.table_widget.item(row, 7).setText(str(item["converted_price"]))
                    self.table_widget.setItem(row, 7, QTableWidgetItem(str(item["sync_at"])))
                    found = True
                    break

            if not found:
                row = self.table_widget.rowCount()
                self.table_widget.insertRow(row)
                name_item = QTableWidgetItem(item["name"])
                name_item.setData(Qt.UserRole, item["listing_id"])  # храним уникальный ID
                self.table_widget.setItem(row, 0, name_item)
                self.table_widget.setItem(row, 1, QTableWidgetItem(str(item["assets"])))
                self.table_widget.setItem(row, 2, QTableWidgetItem(str(item["float"])))
                self.table_widget.setItem(row, 3, QTableWidgetItem(str(item["pattern"])))
                self.table_widget.setItem(row, 7, QTableWidgetItem(str(item["sync_at"])))

                inspect_button = QPushButton("Inspect")
                inspect_button.setCursor(Qt.PointingHandCursor)
                inspect_button.clicked.connect(lambda _, url=item["inspect_link"]: webbrowser.open(url))
                self.table_widget.setCellWidget(row, 5, inspect_button)

                buy_button = QPushButton("Buy")
                buy_button.setCursor(Qt.PointingHandCursor)
                buy_button.clicked.connect(lambda _, url=item["buy_url"]: webbrowser.open(url))
                self.table_widget.setCellWidget(row, 6, buy_button)
            
            # ---- Подсветка строки, если нужно ----
            # if item['is_highlighted']:
            #     for col in range(self.table_widget.columnCount()):
            #         cell_item = self.table_widget.item(row, col)
            #         if cell_item:
            #             cell_item.setBackground(QColor("#25A550"))  # светло-жёлтая подсветка
            #             cell_item.setForeground(QColor("#000000"))  # черный текст

    def update_table(self, items: list):
        self.table_widget.setRowCount(0)

        self.add_or_update_rows(items)

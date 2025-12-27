from PyQt5.QtWidgets import (QWidget, QTableWidget, QHeaderView, QGroupBox, QVBoxLayout, QTableWidgetItem, QPushButton)
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import webbrowser
from qt.style import StyleManager
from PyQt5.QtGui import QColor
from qt.signals import table_dispatcher
from qt.widgets.components.cells import AssetsCellWidget, ItemCellWidget
from qt.widgets.components.buttons import PushButton

# Items table
class ItemsTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        table_dispatcher.items_table.connect(self.add_rows)

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table_widget = QTableWidget(0, 9)
        self.table_widget.setStyleSheet(StyleManager.get_style("QTable"))
        self.table_widget.setHorizontalHeaderLabels(
            ["Name", "Assets", "Price", "Float", "Pattern", "Sync At", "Inspect", "Steam", "Actions"]
        )

        header = self.table_widget.horizontalHeader()

        # Настроим размеры колонок
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Assets
        # header.setMaximumSectionSize(300) 
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Price

        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Float
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Pattern
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
            
            # Старая версия
            # name_item = QTableWidgetItem(item["name"])
            # name_item.setData(Qt.UserRole, item["listing_id"])  # храним уникальный ID
            # self.table_widget.setItem(0, 0, name_item)

            item_name_cell = ItemCellWidget(item["image"], item["name"])
            self.table_widget.setCellWidget(0, 0, item_name_cell)
            # Assets
            assets_widget = AssetsCellWidget(item["assets"])
            self.table_widget.setCellWidget(0, 1, assets_widget)
            self.table_widget.setRowHeight(0, 45)
            self.table_widget.setItem(0, 2, QTableWidgetItem(str(item["converted_price"])))
            self.table_widget.setItem(0, 3, QTableWidgetItem(str(item["float"])))
            self.table_widget.setItem(0, 4, QTableWidgetItem(str(item["pattern"])))
            self.table_widget.setItem(0, 5, QTableWidgetItem(str(item["sync_at"])))

            inspect_button = PushButton("Inspect")
            inspect_button.setCursor(Qt.PointingHandCursor)
            inspect_button.clicked.connect(lambda _, url=item["inspect_link"]: webbrowser.open(url))
            self.table_widget.setCellWidget(0, 6, inspect_button)

            buy_button = PushButton("Buy")
            buy_button.setCursor(Qt.PointingHandCursor)
            buy_button.clicked.connect(lambda _, url=item["buy_url"]: webbrowser.open(url))
            self.table_widget.setCellWidget(0, 7, buy_button)

             # Remove — ★ new ★
            remove_button = PushButton("Remove")
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

# Proxies table
class ProxiesTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._row_by_key: dict[str, int] = {}
        self._init_ui()

        table_dispatcher.proxies_table_insert.connect(self.insert_rows)
        table_dispatcher.proxies_table_update.connect(self.update_rows)

    # ---------------- UI ---------------- #

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 7)
        self.table.setStyleSheet(StyleManager.get_style("QTable"))
        self.table.setHorizontalHeaderLabels([
            "IP", "Port", 
            "Username", "Password",
            "Success rate", "Total Requests", "Last used at"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        box = QGroupBox(" Proxies ")
        box_layout = QVBoxLayout(box)
        box_layout.addWidget(self.table)
        layout.addWidget(box)

    # ---------------- Public API ---------------- #

    def insert_rows(self, rows: list[dict]):
        """
        Добавляет ТОЛЬКО новые строки
        """
        for row in rows:
            key = self._key(row)
            if key in self._row_by_key:
                continue

            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self._row_by_key[key] = row_idx

            self._fill_row(row_idx, row)

    def update_rows(self, rows: list[dict]):
        """
        Обновляет существующие строки
        """
        for row in rows:
            key = self._key(row)
            row_idx = self._row_by_key.get(key)

            if row_idx is None:
                continue  # защита

            self._fill_row(row_idx, row)

    def reset_table(self):
        self.table.setRowCount(0)
        self._row_by_key.clear()

    # ---------------- Internals ---------------- #

    def _fill_row(self, row: int, data: dict):
        self._set(row, 0, data['ip'])
        self._set(row, 1, data['port'])
        self._set(row, 2, data.get('username'))
        self._set(row, 3, data.get('password'))
        # Statistic: отображаем и храним числовое значение для сортировки
        stat = data.get('success_rate')
        self._set(row, 4, self._format_stat(stat))
        item = self.table.item(row, 4)
        if item:
            item.setData(Qt.UserRole, stat if stat is not None else -1)  # для сортировки

        self._set(row, 5, data.get('total_requests', 0))
        self._set(row, 6, self._format_time(data.get('last_used_at')))

        # ---------------- Цветовая подсветка ---------------- #
        self._update_row_color(row, data.get('success_rate'))

    # ---------------- Цветовая подсветка ---------------- #
    def _update_row_color(self, row: int, stat):
        colors = {
            "success": "#28a745",
            "warning": "#d7ba7d",
            "error": "#f48771",
            "default": self.table.palette().base().color().name()
        }

        if stat is None:
            color = colors["default"]
        elif stat >= 80:
            color = colors["success"]
        elif stat < 30:
            color = colors["error"]
        else:
            color = colors["warning"]

        # Применяем цвет ко всем ячейкам строки
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(QColor(color))
            
    def _set(self, row: int, col: int, value):
        item = self.table.item(row, col)
        if item is None:
            item = QTableWidgetItem()
            self.table.setItem(row, col, item)

        item.setText("" if value is None else str(value))

    @staticmethod
    def _key(row: dict) -> str:
        return f"{row['ip']}:{row['port']}"

    @staticmethod
    def _format_stat(stat):
        if not stat:
            return "—"
        return f"{stat}%"
    
    @staticmethod
    def _format_time(dt):
        if not dt:
            return "—"
        return dt.strftime("%H:%M:%S")


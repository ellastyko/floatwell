from PyQt5.QtWidgets import (QWidget, QTableWidget, QHeaderView, QVBoxLayout, QTableWidgetItem)
from PyQt5.QtCore import Qt, QPoint
from qt.style import StyleManager
from PyQt5.QtGui import QColor
from qt.widgets.components.cells import AssetsCellWidget, ItemCellWidget
from qt.widgets.components.cards import ItemFloatingPreview
from core.repositories import listings_repository, proxy_repository
from utils.market import format_price

# Items table
class ItemsTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

        listings_repository.added.connect(self.add_rows)

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.table_widget = QTableWidget(0, 6)
        self.table_widget.setStyleSheet(StyleManager.get_style("QTable"))
        self.table_widget.setHorizontalHeaderLabels(["Name", "Assets", "Price", "Float", "Pattern", "Sync At"])

        header = self.table_widget.horizontalHeader()

        # Настроим размеры колонок
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Assets
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Price

        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Float
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Pattern
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Sync At

        self.table_widget.setColumnWidth(5, 120)  # меньше, чем растягиваемые колонки
        # Фиксируем ширину для кнопок и Sync At
        self.table_widget.setColumnWidth(6, 96)
        layout.addWidget(self.table_widget)

        # ---------- Preview ----------
        self.preview = ItemFloatingPreview(self)

        # ---------- Signals ----------
        self.table_widget.cellClicked.connect(self.show_preview)
        self.table_widget.verticalScrollBar().valueChanged.connect(
            self.preview.animated_hide
        )
        self.table_widget.horizontalScrollBar().valueChanged.connect(
            self.preview.animated_hide
        )

    def add_rows(self, items: list[dict]):
        for item in items:
            self._add_row(item)

    def _add_row(self, item: dict):
        row = 0
        self.table_widget.insertRow(row)

        # 🔑 META ITEM (привязка данных к строке)
        meta_item = QTableWidgetItem()
        meta_item.setData(Qt.UserRole, item)
        self.table_widget.setItem(row, 0, meta_item)

        # Name
        self.table_widget.setCellWidget(
            row, 0,
            ItemCellWidget(item["image"], item["name"])
        )

        # Assets
        self.table_widget.setCellWidget(
            row, 1,
            AssetsCellWidget(item["assets"])
        )

        self.table_widget.setRowHeight(row, 46)

        self.table_widget.setItem(row, 2, QTableWidgetItem(
            f"{format_price(item["converted_price"], item["currency"]['code'], 'uk_UA')} ({item['pricediff'] * 100:.1f}%)"
        ))
        self.table_widget.setItem(row, 3, QTableWidgetItem(
            f"{item['float']:.5f}"
        ))

        # print(item.get('has_rare_pattern'), item['pattern'], item['patterninfo'])
        
        self.table_widget.setItem(row, 4, QTableWidgetItem(
            str(f"{item['pattern']} ({item['patterninfo']['rank']})" if item.get('has_rare_pattern') else item['pattern'])
        ))
        self.table_widget.setItem(row, 5, QTableWidgetItem(
            str(item["sync_at"])
        ))

    def show_preview(self, row, col):
        item = self.table_widget.item(row, 0)
        if not item:
            return

        data = item.data(Qt.UserRole)
        if not data:
            return
        
        rect = self.table_widget.visualItemRect(self.table_widget.item(row, col))
        global_pos = self.table_widget.viewport().mapToGlobal(rect.topRight())
        self.preview.show_data(data, global_pos + QPoint(10, 0))

        
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

        proxy_repository.added.connect(self.insert_rows)
        proxy_repository.updated.connect(self.update_rows)

    # ---------------- UI ---------------- #

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.table = QTableWidget(0, 7)
        self.table.setStyleSheet(StyleManager.get_style("QTable"))
        self.table.setHorizontalHeaderLabels([
            "IP", "Port", "Username", "Password", "Success rate", "Total Requests", "Last used at"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

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


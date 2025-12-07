from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QDockWidget
from PyQt5.QtCore import Qt
from configurator import config
from qt.widgets.sidebar import SidebarDock
from qt.widgets.main import MainWidget
from qt.widgets.status import StatusBar
from qt.controllers import ParserController
from qt.signals import data_bus

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_ui()
        # GUI элементы
        self.setup_ui()

    def _init_ui(self):
        self.setWindowTitle(config['main']['appname'])
        self.setStyleSheet("background-color: #292A2D; color: #f8faff;")

        windowcfg = config['window']
        l_indent, t_indent = windowcfg['indent']
        self.setGeometry(l_indent, t_indent, windowcfg['width'], windowcfg['height'])
        self.setMinimumSize(windowcfg['minw'], windowcfg['minh'])
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        self.mainWidget     = MainWidget()
        layout.addWidget(self.mainWidget, stretch=7)

        self.dockw = SidebarDock('Controller', self)
        self.dockw.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockw)
        self.dockw.setContextMenuPolicy(Qt.PreventContextMenu)

        # Статус бар
        status_bar = StatusBar()
        self.setStatusBar(status_bar)

        self.parser = ParserController()

        # соединяем данные парсера → обновление таблицы
        self.parser.new_data.connect(self.on_new_data)

        self.parser.start()   # запускаем парсер при старте приложения

    def on_new_data(self, item_data):
        data_bus.add_items.emit(item_data)
        
        # self.items_table.update_row(item_data)

    def closeEvent(self, event):
        super().closeEvent(event)
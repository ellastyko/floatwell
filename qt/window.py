from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QDockWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSystemTrayIcon as QTI
from PyQt5 import QtWidgets, QtGui, QtCore
from configurator import config
from qt.widgets.sidebar import SidebarDock
from qt.widgets.main import MainWidget
from qt.widgets.status import StatusBar
from utils.helpers import resource_path
from core.telegram import TelegramBotService
from core.proxy import proxy_service
from core.repositories import proxy_repository
from qt.style import StyleManager

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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        central_widget.setLayout(layout)

        self.mainWidget     = MainWidget()
        layout.addWidget(self.mainWidget, stretch=9)

        self.dockw = SidebarDock('Controller', self)
        self.dockw.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockw)
        self.dockw.setContextMenuPolicy(Qt.PreventContextMenu)

        self._setup_proxies()

        # Статус бар
        status_bar = StatusBar()
        self.setStatusBar(status_bar)

        self.setup_tray()
        

    def setup_tray(self):
        # Иконка трея
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(resource_path(config['main']['icon'])))

        # Меню трея
        self.tray_menu = QtWidgets.QMenu()
        self.tray_menu.setStyleSheet(StyleManager.get_style("QMenu"))

        # Название приложения (disabled item)
        title_action = QtWidgets.QAction("Float Flower", self.tray_menu)
        title_action.setEnabled(False)
        self.tray_menu.addAction(title_action)

        # Exit
        quit_action = QtWidgets.QAction("Exit", self.tray_menu)
        quit_action.triggered.connect(QtWidgets.qApp.quit)
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(None)

        # Обработка кликов
        self.tray_icon.activated.connect(self.on_tray_activated)

        self.tray_icon.show()
    
    def on_tray_activated(self, reason):
        if reason == QTI.Trigger:  # ЛКМ
            self.show()
            self.raise_()
            self.activateWindow()
        elif reason == QTI.Context:  # ПКМ
            cursor = QtGui.QCursor.pos()
            menu_size = self.tray_menu.sizeHint()

            # Меню над курсором (справа-сверху от иконки)
            pos = QtCore.QPoint(
                cursor.x(),
                cursor.y() - menu_size.height()
            )

            self.tray_menu.popup(pos)

    def closeEvent(self, event):
        """Скрываем окно вместо выхода"""
        event.ignore()
        self.hide()

    # Add proxies to table
    def _setup_proxies(self):
        proxy_repository.upsert(proxy_service.proxies)
        # applog.log_message.emit('Proxies added', 'info')

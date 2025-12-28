from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtCore import Qt, QDateTime, pyqtSlot
from qt.signals import applog
from qt.style import StyleManager

class LogWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = applog
        self._init_ui()
        self._setup_style()
        
        # Подключаем сигналы к слотам
        self.signals.log_message.connect(self._append_log_message, Qt.QueuedConnection)
        self.signals.clear_logs.connect(self._clear_logs, Qt.QueuedConnection)
        self._append_log_message('Logger initialized!', 'success')
        
    def _init_ui(self):
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setUndoRedoEnabled(False)
        self.document().setMaximumBlockCount(1000)
        self.setFont(QFont("Consolas", 10))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def _setup_style(self):
        self.setStyleSheet(StyleManager.get_style("QLogWidget"))
    
    @pyqtSlot(str, str)
    def _append_log_message(self, message, level="info"):
        """Слот для безопасного добавления лога из другого потока"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
        
        colors = {
            "success": "#28a745",
            "debug": "#569cd6",
            "info": "#d4d4d4",
            "warning": "#d7ba7d",
            "error": "#f48771",
            "critical": "#ff0000"
        }
        
        color = colors.get(level.lower(), "#d4d4d4")
        html = f"""
        <div style="margin-bottom: 2px;">
            <span style="color: #6a9955;">[{timestamp}]</span>
            <span style="color: {color};">{message}</span>
        </div>
        """
        
        self.append(html)
        self.moveCursor(QTextCursor.End)
    
    @pyqtSlot()
    def _clear_logs(self):
        """Слот для безопасной очистки логов из другого потока"""
        self.clear()
    
    def add_log(self, message, level="info"):
        """Потокобезопасное добавление лога"""
        self.signals.log_message.emit(message, level)
        
    def clear_logs(self):
        """Потокобезопасная очистка логов"""
        self.signals.clear_logs.emit()
    
    def _show_context_menu(self, position):
        menu = self.createStandardContextMenu()
        
        clear_action = menu.addAction("Clean logs")
        clear_action.triggered.connect(self.clear_logs)
        
        copy_action = menu.addAction("Copy all")
        copy_action.triggered.connect(self._copy_all)
        
        menu.exec_(self.viewport().mapToGlobal(position))
        
    def _copy_all(self):
        self.selectAll()
        self.copy()
        self.moveCursor(QTextCursor.End)
        
    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
        else:
            super().wheelEvent(event)



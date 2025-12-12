# utils/window.py
from PyQt5.QtCore import QObject, pyqtSignal
import win32gui, win32con, win32process, os

class WindowDispatcher(QObject):
    request_focus = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.request_focus.connect(self._focus_window)

    def _focus_window(self):
        pid = os.getpid()

        def enum_windows(hwnd, _):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                return False
            return True

        win32gui.EnumWindows(enum_windows, None)

dispatcher = WindowDispatcher()

def focus():
    # вызываем через сигнал — выполнится в главном потоке PyQt
    dispatcher.request_focus.emit()

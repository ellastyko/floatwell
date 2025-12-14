from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from windows_toasts import Toast, WindowsToaster, ToastDisplayImage, ToastDuration
from configurator import config
from utils.helpers import resource_path
from utils.window import focus

class NotificationSignals(QObject):
    notify = pyqtSignal(str, str, ToastDuration)

class Notifier(QObject):
    def __init__(self):
        super().__init__()
        self.signals = NotificationSignals()
        self.toaster = WindowsToaster(config['main']['appname'])
        self.signals.notify.connect(self._show_notification, Qt.QueuedConnection)

    @pyqtSlot(str, str, ToastDuration)
    def _show_notification(self, title, message, duration):
        toast = Toast()
        toast.AddImage(ToastDisplayImage.fromPath(resource_path(config['main']['icon'])))
        toast.text_fields = [title, message]
        toast.duration = duration

        # правильный вызов focus
        toast.on_activated = lambda args: focus()

        self.toaster.show_toast(toast)

    def send(self, title, message, duration):
        self.signals.notify.emit(title, message, duration)

# глобальный экземпляр
notifier = Notifier()

def short_notify(title, message):
    notifier.send(title, message, ToastDuration.Short) 

def long_notify(title, message):
    notifier.send(title, message, ToastDuration.Long) 

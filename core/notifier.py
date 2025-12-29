from PyQt5.QtCore import QObject
from windows_toasts import Toast, WindowsToaster, ToastDisplayImage
from configurator import config
from utils.helpers import resource_path
from utils.window import focus

class Notifier(QObject):
    def __init__(self):
        super().__init__()
        self.enabled = True
        self.toaster = WindowsToaster(config['main']['appname'])

    def notify(self, title, message, duration):
        if not self.enabled:
            return

        toast = Toast()
        toast.AddImage(
            ToastDisplayImage.fromPath(resource_path(config['main']['icon']))
        )
        toast.text_fields = [title, message]
        toast.duration = duration
        toast.on_activated = lambda args: focus()

        self.toaster.show_toast(toast)

notifier = Notifier() 
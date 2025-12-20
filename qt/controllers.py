from PyQt5.QtCore import QThread
from PyQt5.QtCore import QObject, pyqtSignal
from qt.workers import ListingWorker
from qt.signals import applog

class ParserController(QObject):
    stopped  = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = ListingWorker()
        self.worker.moveToThread(self.thread)

        # когда поток стартует → запускаем метод parsera
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_worker_finished)

    def start(self):
        # print('controller start')
        self.thread.start()
        applog.log_message.emit('Listing worker starting...', 'warning')

    
    def stop(self):
        # print('controller stop')
        self.worker.stop()  # сигнал воркеру завершиться

    def on_worker_finished(self):
        # print('on_worker_finished')
        self.thread.quit()
        self.thread.wait()
        self.stopped.emit()
        applog.log_message.emit('Listing worker stopped.', 'warning')
    
parser = ParserController()

from PyQt5.QtCore import QThread
from PyQt5.QtCore import QObject, pyqtSignal
from qt.workers import ListingWorker

class ParserController(QObject):
    stopped  = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = ListingWorker()
        self.worker.moveToThread(self.thread)

        # когда поток стартует → запускаем метод parsera
        self.thread.started.connect(self.worker.run)

    def start(self):
        self.thread.start()
    
    def stop(self):
        self.worker.stop()  # сигнал воркеру завершиться

    def on_worker_finished(self):
        self.thread.quit()
        self.thread.wait()
        self.stopped.emit()
    
parser = ParserController()

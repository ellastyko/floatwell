from PyQt5.QtCore import QThread
from PyQt5.QtCore import QObject, pyqtSignal
from qt.workers import ParserWorker

class ParserController(QObject):
    new_data = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = ParserWorker()
        self.worker.moveToThread(self.thread)

        # когда поток стартует → запускаем метод parsera
        self.thread.started.connect(self.worker.run)

        # данные идут наружу
        self.worker.data_parsed.connect(self.new_data.emit)

    def start(self):
        self.thread.start()

    def stop(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()

from utils.helpers import load_json_resource
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import logging

class SourceManager(QObject):
    BASE_DIR = './sources/'
    
    source_changed = pyqtSignal(str)
    source_error = pyqtSignal(str)  # Сигнал об ошибке
    source_loaded = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.source = None
        self.source_valid = False
        self.source_name = None
        self.source_changed.connect(self._on_source_change)
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)

    def _on_source_change(self, source_name):
        """Загружает новый источник и проверяет его валидность"""
        try:
            self.source_name = source_name
            file_path = self.BASE_DIR + source_name

            # Загрузка JSON
            self.source = load_json_resource(file_path)
            
            if self.source is None:
                raise ValueError(f"Не удалось загрузить файл '{file_path}'")
            
            # Базовая проверка структуры
            self._validate_source()
            
            self.source_valid = True
            self.source_loaded.emit(True, source_name)
        except Exception as e:
            self.source_valid = False
            self.source_loaded.emit(False, source_name)
            self.source_error.emit(f"Ошибка загрузки источника '{source_name}': {str(e)}")

    def _validate_source(self):
        """Проверяет минимальную структуру источника"""
        if not isinstance(self.source, dict):
            raise ValueError("Источник должен быть словарем")
        
        if 'settings' not in self.source:
            raise ValueError("Отсутствует ключ 'settings'")
        
        if 'configurations' not in self.source:
            raise ValueError("Отсутствует ключ 'configurations'")

    def get_settings(self):
        """Получает настройки источника"""
        if not self.source_valid or self.source is None:
            self.logger.warning("Попытка получить настройки из невалидного источника")
            return {}
        
        return self.source.get('settings', {})

    def get_filters(self):
        """Получает фильтры из настроек"""
        settings = self.get_settings()
        return settings.get('filters', {})

    def get_configurations(self):
        """Получает данные из источника"""
        if not self.source_valid or self.source is None:
            self.logger.warning("Попытка получить данные из невалидного источника")
            return []
        
        return self.source.get('configurations', {})

    def is_source_valid(self):
        """Проверяет, загружен ли валидный источник"""
        return self.source_valid

    def get_current_source_name(self):
        """Возвращает имя текущего источника"""
        return self.source_name

# Глобальный экземпляр
source_manager = SourceManager()
from utils.helpers import load_json_resource

class SourceManager:
    def __init__(self):
        super().__init__()
        self.source = None
        self.source_valid = False
        self.source_name = None

    def set_source(self, name, path):
        """Загружает новый источник и проверяет его валидность"""
        try:
            self.source_name = name

            # Загрузка JSON
            self.source = load_json_resource(path)
            
            if self.source is None:
                raise ValueError(f"Не удалось загрузить файл '{path}'")
            
            # Базовая проверка структуры
            self._validate_source()
            
            self.source_valid = True
        except Exception as e:
            self.source_valid = False

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
            print("Попытка получить настройки из невалидного источника")
            return {}
        
        return self.source.get('settings', {})

    def get_filters(self):
        """Получает фильтры из настроек"""
        settings = self.get_settings()
        return settings.get('filters', {})

    def get_configurations(self):
        """Получает данные из источника"""
        if not self.source_valid or self.source is None:
            print("Попытка получить данные из невалидного источника")
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
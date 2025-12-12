from utils.helpers import load_json_resource, save_json_resource
from PyQt5.QtCore import QObject, pyqtSignal
from configurator import config
import json
from typing import Any, Optional

class SettingsManager(QObject):
    """Менеджер настроек с фиксированным путем из конфигуратора"""
    
    # Сигналы
    settings_loaded = pyqtSignal(bool)  # Загрузка завершена (успех)
    settings_updated = pyqtSignal()     # Настройки обновлены
    settings_error = pyqtSignal(str)    # Ошибка
    
    def __init__(self):
        super().__init__()
        self._settings = {}
        self._settings_path = config['configs']['settings']  # Фиксированный путь
        self._load_settings()
    
    def _load_settings(self) -> bool:
        """Загружает настройки из фиксированного пути"""
        try:
            data = load_json_resource(self._settings_path)
            
            if data is None:
                print(f"Файл настроек не найден: {self._settings_path}")
                data = {}  # Создаем пустые настройки
            
            if not isinstance(data, dict):
                raise ValueError("Настройки должны быть словарем")
            
            self._settings = data
            self.settings_loaded.emit(True)
            return True
            
        except Exception as e:
            error_msg = f"Ошибка загрузки настроек: {str(e)}"
            print(error_msg)
            self._settings = {}  # Сбрасываем к пустому словарю
            self.settings_loaded.emit(False)
            self.settings_error.emit(error_msg)
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получает значение по ключу (поддерживает вложенные ключи через точку)
        
        Примеры:
            get('api.key')
            get('ui.theme', 'dark')
        """
        if not self._settings:
            return default
        
        keys = key.split('.')
        value = self._settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Устанавливает значение по ключу и сохраняет в файл
        
        Пример:
            set('api.timeout', 30)
        """
        if not self._settings:
            self._settings = {}
        
        keys = key.split('.')
        data = self._settings
        
        try:
            # Проходим по всем ключам кроме последнего
            for k in keys[:-1]:
                if k not in data:
                    data[k] = {}
                data = data[k]
            
            # Устанавливаем значение
            data[keys[-1]] = value
            
            # Сохраняем в файл
            return self._save()
            
        except Exception as e:
            print(f"Ошибка установки значения {key}: {str(e)}")
            return False
    
    def _save(self) -> bool:
        """Сохраняет настройки в файл"""
        try:
            success = save_json_resource(self._settings_path, self._settings)
            
            if success:
                self.settings_updated.emit()
                print(f"Настройки сохранены в {self._settings_path}")
            
            return success
            
        except Exception as e:
            error_msg = f"Ошибка сохранения настроек: {str(e)}"
            print(error_msg)
            self.settings_error.emit(error_msg)
            return False
    
    def update_batch(self, updates: dict) -> bool:
        """
        Обновляет несколько настроек за раз
        
        Пример:
            update_batch({'api': {'timeout': 30}, 'ui': {'theme': 'dark'}})
        """
        try:
            self._merge_dicts(self._settings, updates)
            return self._save()
        except Exception as e:
            print(f"Ошибка массового обновления: {str(e)}")
            return False
    
    def _merge_dicts(self, target: dict, source: dict) -> None:
        """Рекурсивное объединение словарей"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dicts(target[key], value)
            else:
                target[key] = value
    
    def get_all(self) -> dict:
        """Возвращает все настройки"""
        return self._settings.copy()
    
    def has(self, key: str) -> bool:
        """Проверяет существование ключа"""
        keys = key.split('.')
        data = self._settings
        
        try:
            for k in keys:
                data = data[k]
            return True
        except (KeyError, TypeError):
            return False
    
    def reload(self) -> bool:
        """Перезагружает настройки из файла"""
        return self._load_settings()
    
    def reset_defaults(self, defaults: dict = None) -> bool:
        """
        Сбрасывает настройки к значениям по умолчанию
        
        Пример:
            reset_defaults({'api': {'timeout': 60}, 'ui': {'theme': 'light'}})
        """
        if defaults is not None:
            self._settings = defaults
        else:
            self._settings = {}
        
        return self._save()


# Глобальный экземпляр - создается сразу
settings_manager = SettingsManager()
from utils.helpers import load_json_resource
from qt.signals import applog
from core.source.validation import SourceValidator, SourceValidationError

class SourceManager:
    def __init__(self):
        self.source        = None
        self.source_valid  = False
        self.source_name   = None
        self.source_path   = None

    # -------------------- public API --------------------

    def set_source(self, name, path):
        """Загружает и валидирует источник"""
        self.source_valid = False
        self.source       = None
        self.source_name  = name
        self.source_path  = path

        try:
            source = load_json_resource(path)

            if source is None:
                raise SourceValidationError(
                    f"Не удалось загрузить источник: {path}"
                )

            # 🔒 Контрактная валидация
            SourceValidator.validate_source(source)

            self.source       = source
            self.source_valid = True

            applog.log_message.emit(
                f"✅ Source '{name}' успешно загружен",
                "success"
            )

        except SourceValidationError as e:
            applog.log_message.emit(
                f"❌ Source '{name}' невалиден: {e}",
                "error"
            )

        except Exception as e:
            applog.log_message.emit(
                f"❌ Ошибка загрузки source '{name}': {e}",
                "error"
            )

    # -------------------- getters --------------------

    def is_source_valid(self) -> bool:
        return self.source_valid

    def get_current_source_name(self):
        return self.source_name

    def get_globals(self) -> dict:
        if not self.source_valid:
            return {}
        return self.source.get('globals', {})

    def get_active_strategies(self) -> list:
        """Возвращает активные стратегии (pattern / float / etc)"""
        return self.get_globals().get('strategies', [])

    def get_assets(self) -> dict:
        if not self.source_valid:
            return {}
        return self.source.get('assets', {})
    
    def get_asset_strategies(self, asset_name: str) -> dict:
        return self.get_assets().get(asset_name, {}).get('strategies', {})

    def get_exterior_aliases(self) -> list:
        """Возвращает список полных названий экстерьеров для текущего источника"""
        if not self.source_valid:
            return []

        return self.get_globals().get('exteriors', {}).keys()
    
    def get_exteriors(self) -> list:
        """Возвращает список полных названий экстерьеров для текущего источника"""
        if not self.source_valid:
            return []

        return self.get_globals().get('exteriors', {})

# Глобальный экземпляр
source_manager = SourceManager()

import json 
import os, sys

def save_json_resource(path: str, data: dict) -> bool:
    """
    Сохраняет данные в JSON файл
    
    Args:
        path: Относительный путь к файлу
        data: Данные для сохранения
        
    Returns:
        bool: Успех операции
    """
    try:
        file_path = resource_path(path)
        
        # Создаем директорию, если ее нет
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=False)
        
        print(f"Файл сохранен: {path}")
        return True
        
    except PermissionError:
        print(f"Ошибка: Нет доступа для записи в файл '{path}'")
        return False
    
    except Exception as e:
        print(f"Неизвестная ошибка при сохранении файла '{path}': {e}")
        return False

def load_json_resource(path):
    try:
        file_path = resource_path(path)  # Получаем полный путь
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути '{path}'")
        # Или используйте логирование:
        # logging.error(f"Файл не найден: {path}")
        return None
    
    except json.JSONDecodeError as e:
        print(f"Ошибка: Неверный формат JSON в файле '{path}': {e}")
        return None
    
    except PermissionError:
        print(f"Ошибка: Нет доступа к файлу '{path}'")
        return None
    
    except Exception as e:
        print(f"Неизвестная ошибка при загрузке файла '{path}': {e}")
        return None

def resource_path(relative_path):
    """Возвращает путь к ресурсу даже внутри exe PyInstaller."""
    try:
        # PyInstaller создаёт временную папку _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

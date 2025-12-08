import json 
import os, sys

def load_json_resource(path):
    """Загружаем интересующие паттерны (int_value) из файла"""
    with open(resource_path(path), "r", encoding="utf-8") as f:
        return json.load(f)

def resource_path(relative_path):
    """Возвращает путь к ресурсу даже внутри exe PyInstaller."""
    try:
        # PyInstaller создаёт временную папку _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

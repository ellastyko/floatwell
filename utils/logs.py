from datetime import datetime
from utils.helpers import resource_path

LOG_FILE = "./storage/logs/app.log"

def log(message: str):
    with open(resource_path(LOG_FILE), "a", encoding="utf-8") as f:
        f.write(f"[{formatted_time()}] {message}\n")

def formatted_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
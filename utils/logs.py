from datetime import datetime
from utils.helpers import resource_path
import json

LOG_FILE = "./storage/logs/app.log"
ENDPOINT_RESPONSE_FILE = "./storage/logs/endpoint.json"

def log(message: str):
    with open(resource_path(LOG_FILE), "a", encoding="utf-8") as f:
        f.write(f"[{formatted_time()}] {message}\n")

def save_response(data: dict):
    with open(resource_path(ENDPOINT_RESPONSE_FILE), "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def formatted_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
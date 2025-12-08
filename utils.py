import json 

def load_config(path):
    """Загружаем интересующие паттерны (int_value) из файла"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def convert_price(price, rate):
    return round(price * rate, 2)

def price_difference(current_price: float, min_price: float):
    if min_price == 0:
        return 0  # защита от деления на ноль
    return (current_price - min_price) / min_price


import requests
from typing import Optional

def send_request(
    url: str,
    proxy: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = 10,
) -> str | None | dict:
    """
    Универсальная функция для отправки HTTP-запросов.
    
    :param url: URL для запроса
    :param proxy: словарь вида {"ip":..., "port":..., "username":..., "password":...}
    :param headers: заголовки
    :param timeout: таймаут в секундах
    """

    # Формирование proxy URL
    proxy_url = None

    proxies = None

    # Формируем словарь для requests
    if proxy:
        ip = proxy.get("ip")
        port = proxy.get("port")
        user = proxy.get("username")
        pwd = proxy.get("password")

        if ip and port:
            if user and pwd:
                proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
            else:
                proxy_url = f"http://{ip}:{port}"

            proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }

    return requests.get(url, headers=headers, proxies=proxies, timeout=timeout)

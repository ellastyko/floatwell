from urllib.parse import quote
import time
from utils.requests import send_request
from utils.logs import log, save_response
from utils.helpers import load_json_resource
from typing import Optional
from qt.signals import applog
import re, json
from typing import List, Dict, Any

# --- Настройка ---
class Listings:
    CURRENCIES_PATH = './assets/currencies.json'
    BASE_URL        = 'https://steamcommunity.com/market/listings/730'

    def __init__(self, error_timeout = 1):
        self.error_timeout = error_timeout

        self.currencies = load_json_resource(self.CURRENCIES_PATH)
    
    def get_currency(self, code: str) -> dict | None:
        """Возвращает запись валюты по коду, например 'USD'."""
        code = code.upper()

        for c in self.currencies:
            if c.get("code") == code:
                return c

        return None

    def extract_pattern(self, asset_properties: list) -> int | None:
        """Достаёт int_value из propertyid = 1"""
        for p in asset_properties:
            if (p.get("propertyid") == 1 or p.get("propertyid") == 3) and "int_value" in p:
                return int(p["int_value"]) 
        return None

    def extract_float(self, asset_properties: list) -> float | None:
        """Достаёт int_value из propertyid = 1"""
        for p in asset_properties:
            if p.get("propertyid") == 2 and "float_value" in p:
                return float(p["float_value"]) 
        return None

    def get_inspect_link(self, listing):
        raw_inspect_link = listing['asset']['market_actions'][0]['link']
        
        return raw_inspect_link.replace("%listingid%", listing['listingid']).replace("%assetid%", listing['asset']['id'])

    def get_assets(self, descriptions: List[Dict[str, Any]]):
        """Возвращает список стикеров/чармов, прикреплённых к предмету."""
        items = []

        for desc in descriptions:
            name = desc.get("name", "")
            html = desc.get("value", "")

            # Определяем тип предметов внутри блока
            if name not in ("sticker_info", "keychain_info"):
                continue

            block_type = "sticker" if name == "sticker_info" else "keychain"

            # Ищем <img ... src="" title="">
            matches = re.findall(
                r'<img[^>]*src="([^"]+)"[^>]*title="([^"]+)"',
                html
            )

            for image, title in matches:
                items.append({
                    "type": block_type,
                    "name": title,
                    "image": image
                })

        return items

    def get(self, hash_name: str, currency_code = 'USD', proxy: Optional[dict] = None):
        try:
            currency = self.get_currency(currency_code)

            url = f"{self.BASE_URL}/{quote(hash_name)}/render?count=100&currency={currency['id']}&norender=1"

            response = send_request(url, proxy)

            if response.status_code != 200:
                log_message = (f"HTTP Request error ({response.status_code}) via proxy {proxy['ip']}:{proxy['port']}" )
                applog.log_message.emit(log_message, 'warning')
                return


            log_message = f"Successful HTTP request via proxy {proxy['ip']}:{proxy['port']} ({response.status_code})"
            applog.log_message.emit(log_message, 'success')
                
            data = response.json()
            
            listinginfo = data.get("listinginfo", None)
            assets = data.get("assets", {}).get("730", {}).get("2", None)

            if not assets or not listinginfo:
                log_message = f"No assets or listinginfo"
                log("No assets or listinginfo" + data.keys())
                applog.log_message.emit(log_message, 'warning')
                return 
            
            results = []

            for listing_id, listing in listinginfo.items():
                if int(listing['asset']['amount']) == 0:
                    continue

                asset_id = listing['asset']['id']

                asset = assets[asset_id]
                props = asset.get("asset_properties", [])
                if not props:
                    continue

                pattern      = self.extract_pattern(props)
                float        = self.extract_float(props)
                inspect_link = self.get_inspect_link(listing)
                assets_list  = self.get_assets(asset['descriptions'])

                # Logging
                log_message = f"{asset['market_hash_name']}; Listing: {listing_id}; Pattern: {pattern}; Float: {float}"
                applog.log_message.emit(log_message, 'info')

                results.append({
                    "name": asset['market_hash_name'],
                    "listing_id": listing_id,
                    "pattern": pattern,
                    "float": float,
                    "price": (int(listing['price']) + int(listing['fee'])) / 100,
                    "converted_price": (int(listing['converted_price']) + int(listing['converted_fee'])) / 100,
                    "currency": currency,
                    'assets': assets_list,
                    'has_keychain': any(item["type"] == "keychain" for item in assets_list),
                    'has_stickers': any(item["type"] == "sticker" for item in assets_list),
                    'buy_url': f"{self.BASE_URL}/{quote(hash_name)}#buylisting|{listing_id}|730|2|{asset_id}",
                    'inspect_link': inspect_link
                })
            return results
        except Exception as e:
            log(f"Error: {e}")

# Класс отвечающий за анализ данных полученных из Listings
class Analyzer:
    EXTERIORS_FULL = {
        "Factory New": "FN",
        "Minimal Wear": "MW",
        "Field-Tested": "FT",
        "Well-Worn": "WW",
        "Battle-Scarred": "BS"
    }

    def __init__(self, config: dict):
        """
        config — словарь вида:
        {
            "Five-SeveN | Heat Treated": {
                "pattern": {
                    "rank0": [...],
                    "rank1": [...],
                },
                "float": {
                    "FN": {"min": 0.0, "max": 0.07},
                    "FT": {"min": 0.07, "max": 0.15},
                }
            },
            ...
        }
        """
        self.config = config

    def get_pattern_info(self, item: str, pattern: int, exterior: str | None) -> bool:
        rules = self.config[item]

        # --- Проверяем паттерн ---
        pattern_rules = rules.get("pattern", {})

        for rank, patternInfo in pattern_rules.items():
            pattern_values = patternInfo.get("pattern_values", [])
            pattern_range  = patternInfo.get("range", [])

            # Мэтч происходит либо по range либо по конкретным паттернам
            pattern_match = (
                pattern in pattern_values
                or (
                    isinstance(pattern_range, list) 
                    and len(pattern_range) == 2 
                    and pattern_range[0] <= pattern <= pattern_range[1]
                )
            )

            if pattern_match:
                price_tolerance = patternInfo["price_tolerance"][self.EXTERIORS_FULL[exterior]] if rules['has_exteriors'] else patternInfo["price_tolerance"]
                # tier = patternInfo.get("range", [])

                return {"is_rear": True, "rank": rank, "price_tolerance": price_tolerance, "value": pattern}  

        return {"is_rear": False, "value": pattern}
    
    def get_float_info(self, item: str, float_value: float, exterior: str | None) -> bool:
        rules = self.config[item]

        # --- Проверяем флоат ---
        float_rules = rules.get("float", {})
        if exterior and exterior in float_rules:
            frange = float_rules[exterior]
            if frange["min"] <= float_value <= frange["max"]:
                return {"is_rear": True, "value": float_value}

        return {"is_rear": False, "value": float_value}



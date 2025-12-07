import requests
import json
from datetime import datetime
from urllib.parse import quote
import time

# --- Настройка ---
class Listings:
    BASE_URL  = 'https://steamcommunity.com/market/listings/730'

    def extract_pattern(self, asset_properties: list) -> int | None:
        """Достаёт int_value из propertyid = 1"""
        for p in asset_properties:
            if p.get("propertyid") == 1 and "int_value" in p:
                return int(p["int_value"]) 
        return None

    def extract_float(self, asset_properties: list) -> float | None:
        """Достаёт int_value из propertyid = 1"""
        for p in asset_properties:
            if p.get("propertyid") == 2 and "float_value" in p:
                return float(p["float_value"]) 
        return None

    def get(self, hash_name: str):
        try:
            url = f"{self.BASE_URL}/{quote(hash_name)}/render?count=100&currency=1&norender=1"

            response = requests.get(url)
            data = response.json()

            if response.status_code != 200:
                if response.status_code == 429:
                    time.sleep(30)
                    return
            
            results = []
            listinginfo = data.get("listinginfo", {})
            assets = data.get("assets", {}).get("730", {}).get("2", {})

            if not assets or not listinginfo:
                print("Нет assets или listinginfo в ответе Steam")
                return

            for listing_id, listing in listinginfo.items():
                asset_id = listing['asset']['id']

                asset = assets[asset_id]
                props = asset.get("asset_properties", [])
                if not props:
                    continue

                pattern = self.extract_pattern(props)
                float   = self.extract_float(props)

                results.append({
                    "name": asset['market_hash_name'],
                    "listing_id": listing_id,
                    "pattern": pattern,
                    "float": float,
                    "price": listing['price'],
                    'assets': None,
                    'buy_url': f"https://steamcommunity.com/market/listings/730/{quote(hash_name)}#buylisting|{listing_id}|730|2|{asset_id}",
                })
            return results
        except Exception as e:
            print("Ошибка:", e)

class Analyzer:
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

    def is_rare_pattern(self, item: str, pattern: int) -> bool:
        if item not in self.config:
            return False

        rules = self.config[item]

        # --- Проверяем паттерн ---
        pattern_rules = rules.get("pattern", {})
        for rank, patterns in pattern_rules.items():
            if pattern in patterns:
                return rank  # редкий по паттерну

        return False
    
    def is_rare_float(self, item: str, exterior: str, float_value: float) -> bool:
        if item not in self.config:
            return False

        rules = self.config[item]

        # --- Проверяем флоат ---
        float_rules = rules.get("float", {})
        if exterior and exterior in float_rules:
            frange = float_rules[exterior]
            if frange["min"] <= float_value <= frange["max"]:
                return True  # редкий по флоату

        return False



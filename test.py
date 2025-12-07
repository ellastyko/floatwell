import requests
import json
from datetime import datetime
from urllib.parse import quote
import asyncio

PATTERN_FILE = "./assets/analizer_config.json"
# --- Настройка ---
LOG_FILE = "./storage/steam_float_pattern_log.txt"

EXTERIORS = [
    # "Factory New",
    # "Minimal Wear",
    "Field-Tested",
    # "Well-Worn",
    # "Battle-Scarred"
]

def log(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def extract_pattern(asset_properties: list) -> int | None:
    """Достаёт int_value из propertyid = 1"""
    for p in asset_properties:
        if p.get("propertyid") == 1 and "int_value" in p:
            return int(p["int_value"]) 
    return None

def load_patterns():
    """Загружаем интересующие паттерны (int_value) из файла"""
    with open(PATTERN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

async def check_item(hash_name: str, patterns: dict):
    try:
        url = f"https://steamcommunity.com/market/listings/730/{quote(hash_name)}/render?count=100&currency=1&norender=1"

        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            if response.status_code == 429:
                await asyncio.sleep(60)
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

            pattern = extract_pattern(props)
            if not pattern:
                continue

            # Перебираем ранги и их значения
            for rank_name, rank_patterns in patterns.items()['patterns']:
                if pattern in rank_patterns:
                    url = f"https://steamcommunity.com/market/listings/730/{quote(hash_name)}#buylisting|{listing_id}|730|2|{asset_id}"

                    log_message = (
                        f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Найден паттерн! "
                        f"Pattern: {pattern} | Rank: {rank_name} | Buy: {url}"
                    )
                    log(log_message)
                    break

        log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - sync finished for {hash_name}')
    except Exception as e:
        print("Ошибка:", e)


async def main():
    patterns = load_patterns()

    while True:
        for item_name in patterns.keys():
            for exterior in EXTERIORS:
                hash_name = f"{item_name} ({exterior})"

                await check_item(hash_name, patterns[item_name])
                await asyncio.sleep(1)

        await asyncio.sleep(120)

if __name__ == "__main__":
    asyncio.run(main())

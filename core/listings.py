from urllib.parse import quote
from utils.requests import send_request
from utils.logs import log
from typing import Optional
from qt.signals import applog
import re
from utils.helpers import load_json_resource, save_json_resource
from typing import List, Dict, Any

# --- Настройка ---
class ListingsParser:
    BASE_URL = 'https://steamcommunity.com/market/listings/730'
    BASE_IMAGE_URL = 'https://community.akamai.steamstatic.com/economy/image'

    def __init__(self, error_timeout = 1):
        self.error_timeout = error_timeout

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
    
    def is_valid_listing(self, listing: dict):
        return (
            listing.get('price', 0) > 0 and
            listing.get('asset', {}).get('amount', '0') != '0' and
            'steam_fee' in listing  # Есть комиссии
        )

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
                    "name": title.replace(':', ' |'),
                    "image": image
                })

        return items

    def get(self, hash_name: str, currency: dict, proxy: Optional[dict] = None, start: int = 0, per_page: int = 100):
        url = f"{self.BASE_URL}/{quote(hash_name)}/render?count={per_page}&currency={currency['id']}&norender=1&start={start}"
        
        try:
            response = send_request(url, proxy)

            if response.status_code != 200:
                log_message = (f"HTTP Request error ({response.status_code}) via proxy {proxy['ip']}:{proxy['port']}" )
                applog.log_message.emit(log_message, 'warning')
                return None, None

            log_message = f"Successful HTTP request via proxy {proxy['ip']}:{proxy['port']} ({response.status_code})"
            applog.log_message.emit(log_message, 'success')
                
            data = response.json()
        except Exception as e:
            log(f"Error: {e}")
            return None, None
        
        # data = load_json_resource('./storage/snapshots/endpoint.json')
        results = []
        total_count = data.get("total_count", 0)

        meta = {
            "total_count": total_count,
            "start": start,
            "per_page": per_page,
            "has_more": (start + per_page) < total_count,
            "page": (start / per_page) + 1
        }

        if total_count == 0:
            log_message = f"Listings not found for {hash_name} | Please update your current config!"
            applog.log_message.emit(log_message, 'error')
            return results, meta

        listinginfo = data.get("listinginfo", None)
        assets = data.get("assets", {}).get("730", {}).get("2", None)

        for listing_id, listing in listinginfo.items():
            if not self.is_valid_listing(listing):
                continue

            asset_id = listing['asset']['id']

            asset = assets[asset_id]
            props = asset.get("asset_properties", [])

            if not props:
                log('No asset properties')
                continue

            results.append({
                "name":            asset['name'],
                "hash_name":       asset['market_hash_name'],
                "type":            asset['type'],
                "image":           f"{self.BASE_IMAGE_URL}/{asset['icon_url']}",
                "listing_id":      listing_id,
                "pattern":         self.extract_pattern(props),
                "float":           self.extract_float(props),
                "price":           (int(listing['price']) + int(listing['fee'])) / 100,
                "converted_price": (int(listing['converted_price']) + int(listing['converted_fee'])) / 100,
                'assets':          self.get_assets(asset['descriptions']),
                'buy_url':         f"{self.BASE_URL}/{quote(hash_name)}#buylisting|{listing_id}|730|2|{asset_id}",
                'inspect_link':    self.get_inspect_link(listing),
                "is_valid":        True,
            })

        return results, meta


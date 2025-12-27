from utils.market import price_difference

# Класс отвечающий за анализ данных полученных из Listings
class ListingAnalyzer:
    def __init__(self, globals: dict, assets: dict):
        # Init global settings
        self.globals           = globals
        self.global_strategies = globals.get('strategies', {})
        self.exteriors         = globals.get('exteriors', [])
        self.aliases           = globals.get('aliases', {})
        # Init assets
        self.assets            = assets
    
    def get_aliased_value(self, field: str, value: str):
        return self.aliases[field][value]

    def _apply_item_strategies(self, name: str):
        strategies = self.assets[name].get('strategies', self.global_strategies)
        self.pattern_strategy = strategies.get('pattern', None)
        self.float_strategy   = strategies.get('float', None)

    def apply(self, name, exterior: str|None, items: list):
        # Apply strategies
        self._apply_item_strategies(name)

        result = []
        # Count min price of items batch
        converted_min_price = (min(i.get('converted_price', float('inf')) for i in items) if items else None)

        for item in items: 
            assets    = item.get('assets', [])
            keychains = []
            stickers  = []

            for a in assets:
                t = a.get("type")
                if t == "keychain":
                    keychains.append(a)
                elif t == "sticker":
                    stickers.append(a)

            patterninfo = self._structure_pattern(item['pattern'], exterior)
            floatinfo   = self._structure_float(item['float'], exterior)

            pricediff = price_difference(item['converted_price'], converted_min_price)

            result.append({
                'hash_name':        item['hash_name'],
                'name':             item['name'],
                'image':            item['image'],
                'exterior':         exterior,
                'hash_name':        item['hash_name'],
                "listing_id":       item['listing_id'],
                "pattern":          item['pattern'],
                "float":            item['float'],
                "price":            item['price'],
                "converted_price":  item['converted_price'],
                'assets':           item['assets'],
                'keychains':        keychains,
                'stickers':         stickers,
                'buy_url':          item['buy_url'],
                'inspect_link':     item['inspect_link'],  

                'pricediff':        pricediff,
                'patterninfo':      patterninfo,
                'floatinfo':        floatinfo,

                'is_price_acceptable': patterninfo.get('price_tolerance', 0) > pricediff if pricediff is not None else False,
                'has_rare_pattern':    patterninfo['is_rear'],
                'has_rare_float':      floatinfo['is_rear'],
                'has_keychain':        bool(keychains),
                'has_stickers':        bool(stickers),
            })
        
        return {
            "items":               result,
            "name":                name,
            "hash_name":           f"{name} ({exterior})" if exterior else name,
            "converted_min_price": converted_min_price,
        }
    
    def _structure_pattern(self, patternval: int, exterior: str | None) -> bool:
        # --- Проверяем паттерн ---
        result = {"is_rear": False, "value": patternval}

        if not self.pattern_strategy:
            return result

        for rank_name, rank_params in self.pattern_strategy.items():
            pattern_values = rank_params.get("values", [])
            pattern_range  = rank_params.get("range", [])

            # Мэтч происходит либо по range либо по конкретным паттернам
            pattern_match = (
                patternval in pattern_values
                or (
                    isinstance(pattern_range, list) 
                    and len(pattern_range) == 2 
                    and pattern_range[0] <= patternval <= pattern_range[1]
                )
            )

            if pattern_match:
                price_tolerance = rank_params["price_tolerance"][exterior] if exterior else rank_params["price_tolerance"]

                result['is_rear'] = True
                result['rank'] = rank_name
                result['price_tolerance'] = price_tolerance

        return result
    
    def _structure_float(self, floatval: float, exterior: str | None) -> bool:
        result = {"is_rear": False, "value": floatval}

        if not self.float_strategy:
            return result
        
        if exterior and exterior in self.float_strategy:
            frange = self.float_strategy[self.exteriors[exterior]]

            if frange["min"] <= floatval <= frange["max"]:
                result['is_rear'] = True

        return result



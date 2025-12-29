def convert_price(price, rate):
    return round(price * rate, 2)

def price_difference(current_price: float, min_price: float):
    if min_price == 0:
        return 0  # защита от деления на ноль
    return (current_price - min_price) / min_price


from babel.numbers import format_currency

def format_price(amount: float, currency_code: str, locale: str = "en_US") -> str:
    try:
        return format_currency(amount, currency_code.upper(), locale=locale)
    except Exception as e:
        # fallback
        return f"{currency_code.upper()} {amount:.2f}"

def match_rule(value: str, rule: str) -> bool:
    """
    Поддержка wildcard:
    - "Charm |%"  -> startswith
    - "%Gold%"    -> contains
    - "%Holo"     -> endswith
    - "Exact"     -> exact
    """
    if not value or not rule:
        return False

    value = value.lower()
    rule = rule.lower()

    if rule.startswith('%') and rule.endswith('%'):
        return rule[1:-1] in value
    if rule.startswith('%'):
        return value.endswith(rule[1:])
    if rule.endswith('%'):
        return value.startswith(rule[:-1])

    return value == rule
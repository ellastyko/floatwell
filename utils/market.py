def convert_price(price, rate):
    return round(price * rate, 2)

def price_difference(current_price: float, min_price: float):
    if min_price == 0:
        return 0  # защита от деления на ноль
    return (current_price - min_price) / min_price
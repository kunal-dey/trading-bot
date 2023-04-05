def maximum_quantity(maximum_investment:float, current_price:int)->int:
    """
        maximum quantity which can be bought so that it remains within the investment level
    """
    quantity:int = int(maximum_investment/current_price)
    if quantity>0:
        return quantity
    return 0
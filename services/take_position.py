from constants.global_contexts import kite_context
from constants.enums.product_type import ProductType

def short(symbol:str, quantity:int, product_type:ProductType):
    """
        takes a short position which means it will
        1. sell the position which has already been bought, or
        2. sell a negative quantity of stocks
    """
    try:
        response_data = kite_context.place_order(
            variety=kite_context.VARIETY_REGULAR,
            order_type=kite_context.ORDER_TYPE_MARKET,
            exchange=kite_context.EXCHANGE_NSE,
            tradingsymbol=symbol,
            transaction_type=kite_context.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            product=kite_context.PRODUCT_MIS if product_type == ProductType.INTRADAY else kite_context.PRODUCT_CNC,
            validity=kite_context.VALIDITY_DAY
        )
        return True     
    except Exception as e:    
        return False

def long(symbol: str, quantity: int, product_type:ProductType):
    """
        takes a long position which means it will
        1. buy the position which has already been short, or
        2. buy a positive quantity of stocks
    """

    try:
        kite_context.place_order(
            variety=kite_context.VARIETY_REGULAR,
            order_type=kite_context.ORDER_TYPE_MARKET,
            exchange=kite_context.EXCHANGE_NSE,
            tradingsymbol=symbol,
            transaction_type=kite_context.TRANSACTION_TYPE_BUY,
            quantity=quantity,
            product=kite_context.PRODUCT_MIS if product_type == ProductType.INTRADAY else kite_context.PRODUCT_CNC,
            validity=kite_context.VALIDITY_DAY
        )
        return True     
    except Exception as e:    
        return False
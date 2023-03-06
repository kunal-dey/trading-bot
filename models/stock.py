from constants.global_contexts import kite_context

class Stock:
    """
        Given a symbol and exchange it holds all the information related to the stock such as price
    """
    def __init__(
            self,
            symbol:str,
            exchange:str
        ) -> None:
        self.stock_name = symbol
        self.exchange = exchange

    @property
    def current_price(self):
        """
            returns the current price in the market or else None if the connection interrupts
        """
        try:
            return kite_context.ltp([f"NSE:{self.stock_name}"])[f"NSE:{self.stock_name}"]["last_price"]
        except:
            return None
from models.stock_stage import Stage
from models.stock import Stock
from models.costs.intraday_trading_cost import IntradayTransactionCost

from constants.enums.position_type import PositionType
from constants.enums.product_type import ProductType

class Position(Stage):

    def __init__(
            self, 
            symbol: str,
            exchange: str,
            position_price: float, 
            quantity: int,
            product_type: ProductType,
            position_type: PositionType,
            order_id:str
            ) -> None:
        
        super().__init__(
            Stock(symbol=symbol, exchange=exchange), 
            position_price, 
            quantity,
            product_type,
            position_type)
        self.order_id = order_id
        
    def transaction_cost(self, buying_price, selling_price)->float:
        return IntradayTransactionCost(
            buying_price=buying_price,
            selling_price=selling_price,
            quantity=self.quantity
        ).total_tax_and_charges



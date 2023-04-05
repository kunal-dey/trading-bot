from models.stock_stage import Stage
from models.stock import Stock
from models.costs.delivery_trading_cost import DeliveryTransactionCost
from models.costs.intraday_trading_cost import IntradayTransactionCost

from constants.enums.position_type import PositionType
from constants.enums.product_type import ProductType

from constants.settings import DELIVERY_INITIAL_RETURN


class Holding(Stage):

    def __init__(
            self, 
            symbol: str,
            exchange: str,
            position_price: float, 
            quantity: int, 
            number_of_days: int) -> None:

        super().__init__(
            Stock(symbol=symbol, exchange=exchange), 
            position_price, 
            quantity, 
            ProductType.DELIVERY,
            PositionType.LONG)

        self.number_of_days = number_of_days

    def transaction_cost(self, buying_price, selling_price)->float:
        if self.number_of_days > 0:
            return DeliveryTransactionCost(
                buying_price=buying_price,
                selling_price=selling_price,
                quantity=self.quantity
            ).total_tax_and_charges
        else:
            return IntradayTransactionCost(
                buying_price=buying_price,
                selling_price=selling_price,
                quantity=self.order.quantity
            ).total_tax_and_charges
        
    @property
    def current_expected_return(self):
        if self.number_of_days > 0:
            return ((1+DELIVERY_INITIAL_RETURN)**(self.number_of_days+1))-1
        else:
            return DELIVERY_INITIAL_RETURN


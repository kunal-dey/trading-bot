from models.stock_stage import Stage
from models.stock import Stock
from models.stock_stages.position import Position

from constants.enums.product_type import ProductType
from constants.enums.position_type import PositionType

from models.costs.intraday_trading_cost import IntradayTransactionCost

class CumulativePosition(Stage):
    def __init__(
            self, 
            stock: Stock, 
            starting_position:Position
        ) -> None:
        self.positions = [Position]
        super().__init__(stock, starting_position.position_price, starting_position.quantity, ProductType.INTRADAY, PositionType.LONG)
    
    def stock_count(self):
        return len(self.positions)

    def update_position(self, position:Position, type="ADD"):
        """
            average buying price or position price is sum_i(b_i*q_i)/sum_i(q_i) 
            where i -> 1 to n
            n being the number of positions
            b_i is the buying price of the ith position
            q_i is the quantity bought for the ith position
        """
        if type == "ADD":
            self.positions.append(position)
        elif type == "REMOVE":
            self.positions.remove(position)
        
        new_total_price = 0
        new_total_quantity = 0

        for position in self.positions:
            new_total_price += position.position_price * position.quantity
            new_total_quantity += position.quantity

        self.position_price = new_total_price/new_total_quantity
        self.quantity = new_total_quantity

    def transaction_cost(self, buying_price, selling_price)->float:
        """
            if f(b, q, s) is an intraday function where b is buying price, q is quantity and s is selling price
            then total transaction cost is sum_i(f(b_i, q_i, s)) where i -> 1 to n where n is number of positions

            here buying price is not required
        """
        total_transaction_cost = 0
        for position in self.positions:
            total_transaction_cost += IntradayTransactionCost(
                buying_price=position.position_price,
                selling_price=selling_price,
                quantity=position.quantity
            )
        return total_transaction_cost
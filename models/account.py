from logging import Logger

from utils.logger import get_logger

from constants.global_contexts import kite_context
from constants.settings import MINIMUM_INVESTMENT

from models.stock_stages.holding import Holding
from models.stock_stages.position import Position
from models.cash_management import CashManager

from models.stock import Stock

from constants.enums.product_type import ProductType
from constants.enums.position_type import PositionType
from services.take_position import long
from services.quantity_to_buy import maximum_quantity

from utils.blacklist_orderid import get_blacklisted_order_id, add_blacklisted_order_id

logger:Logger = get_logger(__name__)

class Account:

    holdings:dict[str, Holding] = {}
    positions:dict[str, list[Position]] = {}

    def __init__(self, cash_manager:CashManager) -> None:
        self.cash_manager = cash_manager
        self.loaded = False
    
    def update_holdings(self):
        """
            Only once during the start, the holdings need to be updated.
            Because, no new holdings will be added for that day.
            All the positions will get converted.

            If any holdings is sold it should be managed in the app.
        """
        for holding_data in kite_context.holdings():
            holding:Holding = Holding(
                symbol=holding_data['tradingsymbol'],
                exchange=holding_data['exchange'],
                position_price=holding_data['average_price'],
                quantity=holding_data['opening_quantity'],
                number_of_days=1
            )
            self.holdings[holding.stock.stock_name] = holding

        # whenever the holdings are updated the total amount of holdings must also update
        self.cash_manager.total_invested_holding_amount = self.holdings

    def delete_holdings(self, holding_name):
        """
            deletes the holding and update the cash invested. Even though it wont be used for that day.
        """
        del self.holdings[holding_name]
        self.cash_manager.total_invested_holding_amount = self.holdings

    def update_positions(self):
        new_orders = kite_context.orders()

        for order in new_orders:
            # if order is not present inside any of the positions then add it else leave it 
            if not self.check_order_present(order_id=order['order_id'], trading_symbol=order['tradingsymbol']):
                if order['transaction_type'] == 'BUY' and order['status'] != 'REJECTED':
                    position:Position = Position(
                            order_id=order['order_id'],
                            symbol=order['tradingsymbol'],
                            exchange='NSE',
                            position_price=order['average_price'],
                            quantity=order['quantity'],
                            product_type=ProductType.DELIVERY,
                            position_type=PositionType.LONG
                        )
                    if position.stock.stock_name in self.positions.keys():
                        self.positions[position.stock.stock_name].append(position)
                    else:
                        self.positions[position.stock.stock_name] = [position]

    def check_order_present(self, order_id:str, trading_symbol:str) -> bool:
        """
            function to check whether order with given order id already present or not
        """
        # when the stock has achieved its target the key will be deleted from the positions so the symbol wont exist

        #if the stock has never being sold and backlisted
        if order_id in get_blacklisted_order_id()["ids"]:
            return True
        
        if trading_symbol not in self.positions.keys():
            return False
    
        for position in self.positions[trading_symbol]:
            if position.order_id == order_id:
                return True
        
        return False

    def delete_position(self, stock_name:str, stocks_to_buy, order_id, cumulative=False):
        for position in  self.positions[stock_name]:
            if  not cumulative:
                if position.order_id == order_id:
                    self.positions[stock_name].remove(position)
                    add_blacklisted_order_id(position.order_id)
                    break
        stocks_to_buy[stock_name] = Stock(stock_name, "NSE")
        return stocks_to_buy
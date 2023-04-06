from models.stock import Stock

from logging import Logger

from utils.logger import get_logger

from constants.enums.position_type import PositionType
from constants.enums.product_type import ProductType

from constants.settings import DELIVERY_INITIAL_RETURN, DELIVERY_INCREMENTAL_RETURN

from services.take_position import long, short

logger:Logger = get_logger(__name__)

class Stage:

    def __init__(
        self,
        stock:Stock,
        position_price:float,
        quantity:int,
        product_type:ProductType,
        position_type:PositionType,
        ) -> None:

        self.stock = stock
        self.position_price = position_price
        self.quantity = quantity
        self.product_type = product_type
        self.position_type = position_type

        self.last_price = self.stock.current_price
        self.trigger = None
        self.max_trigger = None

    @property
    def invested_amount(self) -> float:
        """
            amount invested in this stock (transaction cost is not included)
        """
        return self.position_price * abs(self.quantity)
    
    def transaction_cost(self, buying_price, selling_price)->float:
        return None
    
    @property
    def current_expected_return(self):
        return DELIVERY_INITIAL_RETURN
    
    def set_trigger(self, stock_price:float):
        """
            in case of cumulative position the cost is given by
            cost = sum_i(b_i*q_i)/sum_i(q_i)  + sum_i(f(b_i, q_i, s))/sum_i(q_i)
            where f is an intraday function
            i -> 1 to n
            n being the number of positions
            b_i is the buying price of the ith position
            q_i is the quantity bought for the ith position

            this can be divided in average buying price(A) + average transaction cost (B)

            Since the cumulative only has LONG as of now so the code for short selling is unchanged
        """
        global logger 
        cost = None
        selling_price:float = None
        buy_price:float = None

        if self.position_type == PositionType.LONG:
            # this handles the A part
            buy_price = self.position_price
            selling_price = stock_price
        else:
            buy_price = stock_price
            selling_price = self.position_price

        # this handles the B part
        tx_cost = self.transaction_cost(
            buying_price=buy_price,
            selling_price=selling_price
        )/self.quantity

        logger.info(f"the total transaction cost for {self.stock.stock_name} is {tx_cost*self.quantity}")

        cost = buy_price+tx_cost

        counter = 1

        self.minimun_return = cost*(1 + self.current_expected_return)

        while cost*(1 + self.current_expected_return + counter*DELIVERY_INCREMENTAL_RETURN) < selling_price:
            if self.position_type == PositionType.SHORT:
                
                self.trigger = selling_price/(1 + self.current_expected_return + (counter-1)*DELIVERY_INCREMENTAL_RETURN)
            else:
                self.trigger = cost*(1 + self.current_expected_return + (counter-1)*DELIVERY_INCREMENTAL_RETURN)
            counter += 1

        if self.max_trigger:
            if self.max_trigger < self.trigger:
                self.max_trigger = self.trigger
            else:
                self.trigger = self.max_trigger
        else:
            self.max_trigger = self.trigger
            
        if self.trigger:

            logger.info(f"current return for {self.stock.stock_name} is  {(self.trigger/cost)-1}")

    def breached(self):
        """
            if current price is less than previous trigger then it sells else it updates the trigger
        """
        global logger

        latest_price = self.stock.current_price # latest price can be None or float 
    
        if latest_price:
            self.last_price = latest_price

        # if position was long then on achieving the trigger it should sell otherwise it should buy
        # to clear the position
        if self.position_type == PositionType.LONG:
            
            logger.info(f"{self.stock.stock_name} Earlier trigger:  {self.trigger}, latest price:{self.last_price}")
            if (self.trigger != None) and (self.minimun_return != None):
                
                if self.last_price < self.minimun_return:
                    self.fallen_more_than_once = False
                    self.trigger = None
                    self.max_trigger = None
                    return False
                # if it hits trigger then square off else reset a new trigger
                if self.last_price < self.max_trigger:
                    if self.fallen_more_than_once:
                        short(symbol=self.stock.stock_name, quantity=self.quantity, product_type=self.product_type)
                        logger.info(f"Selling {self.stock.stock_name} at {self.last_price} Quantity:{self.quantity}")
                        return True
                    else:
                        self.fallen_more_than_once = True
                        return False
                # if the price fall below trigger and bounced back then self.fallen has to be false
                else:
                    self.fallen_more_than_once=False
            self.set_trigger(self.last_price)
            return False
        else:
            logger.info(f"{self.stock.stock_name} Earlier trigger:  {self.trigger}, last price:{self.last_price}")
            if self.trigger and self.minimun_return:
                if self.position_price > self.minimun_return:
                    self.fallen_more_than_once = False
                    self.trigger = None
                    self.max_trigger = None
                    return False
                # if it hits trigger then square off else reset a new trigger
                if self.last_price > self.max_trigger:
                    if self.fallen_more_than_once:
                        logger.info(f"Buying {self.stock.stock_name} at {self.last_price} Quantity:{self.quantity}")
                        long(symbol=self.stock.stock_name, quantity=self.quantity, product_type=self.product_type)
                        return True
                    else:
                        self.fallen_more_than_once = True
                        return False
                # if the price fall below trigger and bounced back then self.fallen has to be false
                else:
                    self.fallen_more_than_once=False
            self.set_trigger(self.last_price)
            return False

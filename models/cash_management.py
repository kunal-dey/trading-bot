import requests
import json
from logging import Logger

from utils.logger import get_logger

from constants.kite_credentials import API_KEY
from constants.global_contexts import kite_context

from models.stock_stages.holding import Holding
from models.stock_stages.position import Position

logger:Logger = get_logger(__name__)

class CashManager:

    __available_cash:float =None
    __total_invested_holding_amount = None
    __total_invested_position_amount = None

    def __init__(self) -> None:
        pass

    def update_initial_cash(self)->None:
        """
            It fetches the amount left in the account at the start of day

            It needs to be run only once to update the __available_cash
        """
        try:
            response = requests.get(
                url="https://api.kite.trade/user/margins",
                headers={
                        "X-Kite-Version":"3",
                        "Authorization":f"token {API_KEY}:{kite_context.access_token}",
                    }
            )
        except:
            response = None
        
        data = json.loads(response.text) if response else None
        self.__available_cash =  float(data["data"]["equity"]["available"]["live_balance"]) if data else None

    @property
    def total_invested_holding_amount(self):
        """
            this property provides the current invested amount in holdings
        """
        return self.__total_invested_holding_amount
    
    @total_invested_holding_amount.setter
    def total_invested_holding_amount(self,holdings: dict[str, Holding]):
        """
            this property updates the current invested amount in holdings
        """
        self.__total_invested_holding_amount = 0
        for holding in holdings.values():
            self.__total_invested_holding_amount += holding.invested_amount

    @property
    def total_invested_position_amount(self):
        """
            this property provide the current invested amount in positions
        """
        return self.__total_invested_position_amount
    
    @total_invested_position_amount.setter
    def total_invested_position_amount(self, positions: dict[str, Position]):
        """
            this property updates the current invested amount in positions
        """
        self.__total_invested_position_amount = 0
        for position in positions.values():
            self.__total_invested_position_amount += position.invested_amount
    
    @property
    def total_invested_amount(self):
        return self.__total_invested_holding_amount + self.__total_invested_position_amount
    
    @property
    def cash_at_hand(self):
        """
            It provides the cash available which can be invested

            One thing to note is that, even if a holding is sold, the cash wont be readily available.
        """
        return self.__available_cash - self.__total_invested_position_amount
    


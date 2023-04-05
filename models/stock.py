from constants.global_contexts import kite_context
import pandas as pd
import numpy as np

from logging import Logger

from utils.logger import get_logger
from time import sleep

logger:Logger = get_logger(__name__)

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
        # self.lowest_price = None
        self.latest_price = None

        self.__result_stock_df:pd.DataFrame = None

    @property
    def current_price(self):
        """
            returns the current price in the market or else None if the connection interrupts
        """
        
        try:
            return kite_context.ltp([f"NSE:{self.stock_name}"])[f"NSE:{self.stock_name}"]["last_price"]
        except:
            return None
        

    def update_price(self):
        """
            for every new price it sets the last price after trying 4 times
        """
        retries = 0
        current_price = None
        while retries < 4:
            current_price = self.current_price
            if current_price:
                break
            retries += 1 
            sleep(1)
        # if current_price:
        #     if self.lowest_price:
        #         if current_price < self.lowest_price:
        #             self.lowest_price = current_price
        #     else:
        #         self.lowest_price = current_price
        self.latest_price = current_price
        self.update_stock_df(self.latest_price)

    def whether_buy(self):
        # retries = 0
        # current_price = None
        # while retries < 4:
        #     current_price = self.current_price
        #     if current_price:
        #         break
        #     retries += 1 
        #     sleep(1)

        # logger.info(f"prices {self.lowest_price} {self.latest_price}")
        df = self.__result_stock_df.copy()
        if df.shape[0] > 22:
            
            df['line'] = self.KAMA(df["price"])
            df['signal'] = df['line'].ewm(span=12).mean()
            df = df.fillna(999)
            returns = df['signal'].pct_change()+1
            if returns.iloc[-1] != 999:
                if returns.iloc[-1] >1 and returns.iloc[-2] <=1 and returns.iloc[-3] <=1:
                    return True
        return False


        # if self.lowest_price and self.latest_price:
        #     if current_price > self.latest_price and self.latest_price > self.lowest_price:
        #         return True
        # else:
        #     return False
        
    def update_stock_df(self, current_price:float):
        try:
            self.__result_stock_df = pd.read_csv(f"temp/{self.stock_name}.csv")
            self.__result_stock_df.drop(self.__result_stock_df.columns[0], axis=1, inplace=True)
        except:
            self.__result_stock_df = None
        stock_df = pd.DataFrame({"price":[current_price]})
        if self.__result_stock_df is not None:
            self.__result_stock_df = pd.concat([self.__result_stock_df, stock_df],ignore_index=True)
        else:
            self.__result_stock_df = stock_df
        self.__result_stock_df.to_csv(f"temp/{self.stock_name}.csv")
        self.__result_stock_df = self.__result_stock_df.fillna(method='bfill').fillna(method='ffill')
        self.__result_stock_df.dropna(axis=1,inplace=True)

    @staticmethod
    def KAMA(price, n=10, pow1=2, pow2=30):
        ''' kama indicator '''    
        ''' accepts pandas dataframe of prices '''

        absDiffx = abs(price - price.shift(1) )  
        abs_price_change = np.abs(price - price.shift(n))
        vol = absDiffx.rolling(n).sum()
        ER = abs_price_change/vol
        fastest_SC, slowest_SC = 2/(pow1+1), 2/(pow2+1)

        sc = (ER*(fastest_SC-slowest_SC)+slowest_SC) ** 2.0


        answer = np.zeros(sc.size)
        N = len(answer)
        first_value = True

        for i in range(N):
            if sc[i] != sc[i]:
                answer[i] = np.nan
            else:
                if first_value:
                    answer[i] = price[i]
                    first_value = False
                else:
                    answer[i] = answer[i-1] + sc[i] * (price[i] - answer[i-1])
        return answer

        
        
    
from datetime import datetime
from asyncio import sleep
from logging import Logger

from utils.logger import get_logger

from models.account import Account
from models.cash_management import CashManager
from models.stock import Stock

from routes.stocks_input import choosen_stocks

from constants.settings import END_TIME, SLEEP_INTERVAL, START_TIME, STOP_BUYING_TIME

logger:Logger = get_logger(__name__)

async def background_task():
    """
        all the tasks mentioned here will be running in the background
    """
    global logger

    logger.info("BACKGROUND TASK STARTED")

    cash_manager:CashManager = CashManager()
    cash_manager.update_initial_cash()

    account: Account = Account(
        cash_manager
    )

    current_time = datetime.now()
    selected_stocks = choosen_stocks()

    stocks_to_buy = {stock:Stock(stock, "NSE") for stock in selected_stocks.keys()}

    stocks_to_track = {stock:Stock(stock, "NSE") for stock in selected_stocks.keys()}

    # account.update_holdings()
    
    while (current_time < END_TIME):
        current_time = datetime.now()
        try:
            await sleep(SLEEP_INTERVAL)
            # holdings_to_delete =[] # this is needed or else it will alter the lenght during loop
    
            # for holding_name in account.holdings.keys():
            #     holding= account.holdings[holding_name]
            #     if holding.breached():
            #         logger.info(f" line 89 -->sell {holding.stock.stock_name}")
            #         holdings_to_delete.append(holding_name)
                
            # for holding_name in holdings_to_delete:
            #     account.delete_holdings(holding_name)
            if (START_TIME < current_time) and (STOP_BUYING_TIME > current_time):
                for stock_name in stocks_to_track.keys():
                    stocks_to_track[stock_name].update_price()
                    if stock_name in list(stocks_to_buy.keys()):
                        stocks_to_buy[stock_name] = stocks_to_track[stock_name]

            account.update_positions()

            delete_positions = {}
            
            for stock_name in account.positions.keys():
                for position in account.positions[stock_name]:
                    if position.breached():
                        logger.info(f" line 75 -->sell {position.stock.stock_name}")
                        delete_positions[stock_name] = position.order_id

            
            for stock_name in delete_positions.keys():
                stocks_to_buy = account.delete_position(stock_name,stocks_to_buy, delete_positions[stock_name])
            
        except:
            logger.exception("Kite error may have happened")


    logger.info("TASK ENDED")

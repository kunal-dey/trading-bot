from datetime import datetime

# expected returns are set in this section
DELIVERY_INITIAL_RETURN = 0.001
DELIVERY_INCREMENTAL_RETURN = 0.0015

DRAWDOWN_ALLOWED = 0.03

# time settings
__current_time = datetime.now()
START_TIME = datetime(__current_time.year,__current_time.month,__current_time.day,9,15,0)
END_TIME = datetime(__current_time.year,__current_time.month,__current_time.day, 15,0)
STOP_BUYING_TIME = datetime(__current_time.year,__current_time.month,__current_time.day, 15,0,0)

SLEEP_INTERVAL = 15

# investment levels
MINIMUM_INVESTMENT = 3000

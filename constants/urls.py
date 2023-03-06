from constants.kite_credentials import API_KEY

REDIRECT_URL = "https://api.kite.trade/portfolio/holdings/authorise"
AUTHORISE_REDIRECT_URL = f"https://kite.zerodha.com/connect/portfolio/authorise/holdings/{API_KEY}/" # add the request id{request_id}
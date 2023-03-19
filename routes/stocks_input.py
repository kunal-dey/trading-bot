from quart import Blueprint, request

stocks_input = Blueprint("stocks_input", __name__)

selected_stocks = {}

@stocks_input.post("/stocks")
async def recieve_stocks():
    """
        this endpoint is used by frontend to update the stocks
    """
    global selected_stocks
    payload = await request.form
    for stock in payload.keys():
        selected_stocks[stock] = int(payload.getlist(stock)[0])
    return {"msg":selected_stocks}

@stocks_input.get("/stocks")
async def get_stocks():
    """
        this endpoint is used to view selected stocks
    """
    global selected_stocks
    return {"msg":selected_stocks}

def choosen_stocks():
    global selected_stocks
    return selected_stocks


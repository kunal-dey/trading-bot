from quart import Quart, request
from quart_cors import cors

from services.background_task import background_task

from constants.global_contexts import set_access_token

app = Quart(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app = cors(app, allow_origin="*")

@app.get("/set")
async def set_token_request():
    try:
        set_access_token(request.args["token"])
        return {"message":"Token set"}
    except:
        return {"message":"there is an error"}

@app.get("/start")
async def start_process():
    try:
        app.add_background_task(background_task)
        return {"message":"Background process started"}
    except:
        return {"message":"Kindly login first"}

@app.route("/stop")
async def stop_background_tasks():
    """
        On being deployed if we need to manually stop the background task then
        this route is used
    """
    for task in app.background_tasks:
        task.cancel()
    return {"message":"All task cancelled"}

if __name__ == "__main__":
    app.run(port=8081)
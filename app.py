from quart import Quart, Blueprint
from quart_cors import cors

from services.background_task import background_task

from routes.login import login
from routes.stocks_input import stocks_input

app = Quart(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app = cors(app, allow_origin="*")

@app.get("/start")
async def start_process():
    """
        this route is used to start the background process. It can be started after the 
        login process is complete
    """
    try:
        app.add_background_task(background_task)
        return {"message":"Background process started"}
    except:
        return {"message":"Kindly login first"}, 400

@app.route("/stop")
async def stop_background_tasks():
    """
        On being deployed if we need to manually stop the background task then
        this route is used
    """
    for task in app.background_tasks:
        task.cancel()
    return {"message":"All task cancelled"}

resource_list:Blueprint=[login, stocks_input]

for resource in resource_list:
    app.register_blueprint(blueprint=resource)

if __name__ == "__main__":
    app.run(port=8080)
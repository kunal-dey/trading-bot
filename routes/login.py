from quart import Blueprint, Response, redirect, request
import json
import requests

from constants.global_contexts import kite_context
from constants.kite_credentials import API_SECRET, API_KEY
from constants.urls import REDIRECT_URL, AUTHORISE_REDIRECT_URL

login = Blueprint("login", __name__)

access_token = None

def authorise()->str:
    """
        In order to go to the authorization page of cdsl, a request key is 
        obtained from the kite
    """
    response:Response = requests.post(
        url=REDIRECT_URL,
        headers={
            "X-Kite-Version":"3",
            "Authorization":f"token {API_KEY}:{kite_context.access_token}",
            },
        data={}
    )
    data = json.loads(response.text) # converting text to json/dict
    return data["data"]["request_id"]

@login.get("/login")
async def login_process()->Response:
    """
        This route is redirect to the login page of kite connect.
    """
    return redirect(location=kite_context.login_url())

@login.get("/home")
async def cdsl_access()->Response:
    """
        localhost/home Route is provided in the kite trade dashboard which
        is the route redirected by kite when login is successful.

        It contains request_token which is used to generate session
        and set kite_context app. the kitecontext app is used
        for buying or selling or getting account info.

        after the token is token, it redirects to the authorization page of CDSL, where all stocks are
        authorized for buy or sell for that day if there are any holdings.
        * the cdsl page is provided by kite
    """

    # getting request token and setting the app with that token
    global access_token

    data = kite_context.generate_session(
        request_token=request.args["request_token"],
        api_secret=API_SECRET
    )
    access_token = data["access_token"]
    kite_context.set_access_token(access_token=access_token)
    # redirecting to the cdsl authorization page
    request_id = authorise()
    return redirect(location=f"{AUTHORISE_REDIRECT_URL}{request_id}")


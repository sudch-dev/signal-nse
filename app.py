from flask import Flask, request, render_template
from kiteconnect import KiteConnect
import os

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

@app.route("/login")
def login():
    return render_template("login.html", api_key=API_KEY)

@app.route("/token", methods=["GET", "POST"])
def token():
    access_token = None
    if request.method == "POST":
        req_token = request.form["request_token"]
        try:
            data = kite.generate_session(req_token, api_secret=API_SECRET)
            access_token = data["access_token"]
        except Exception as e:
            access_token = f"Error: {e}"
    return render_template("token.html", access_token=access_token)

@app.route("/signal")
def signal():
    symbol = "NSE:HDFCBANK"
    try:
        quote = kite.ltp(symbol)[symbol]
        price = quote["last_price"]
        volume = quote["volume"]
        signal_msg = "Live price fetched successfully."
    except Exception as e:
        price = "₹-"
        volume = "-"
        signal_msg = f"Error: {e}"
    return render_template("signal.html", price=price, volume=volume, signal=signal_msg)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
from flask import Flask, request, render_template
import os
from kiteconnect import KiteConnect
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
kite = KiteConnect(api_key=API_KEY)

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
            with open("access_token.txt", "w") as f:
                f.write(access_token)
        except Exception as e:
            access_token = f"Error: {e}"
    return render_template("token.html", access_token=access_token)

@app.route("/signal", methods=["GET", "POST"])
def signal():
    symbols = ["HDFCBANK", "RELIANCE", "INFY", "TCS", "ICICIBANK"]
    data = None
    if request.method == "POST":
        symbol = request.form["symbol"]
        try:
            with open("access_token.txt") as f:
                kite.set_access_token(f.read().strip())
            quote = kite.ltp(f"NSE:{symbol}")
            price = quote[f"NSE:{symbol}"]["last_price"]
            volume = quote[f"NSE:{symbol}"].get("volume", "N/A")
            signal = "Buy" if price % 2 == 0 else "Sell"
            data = {"price": price, "volume": volume, "signal": signal}
        except Exception as e:
            data = {"price": "-", "volume": "-", "signal": f"Error: {e}"}
    return render_template("signal.html", symbols=symbols, data=data)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, redirect, request, render_template
from kiteconnect import KiteConnect
import os

app = Flask(__name__)

API_KEY = os.environ.get("KITE_API_KEY")
API_SECRET = os.environ.get("KITE_API_SECRET")
kite = KiteConnect(api_key=API_KEY)

nse_100_symbols = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "ITC",
    "HINDUNILVR", "BHARTIARTL", "ASIANPAINT", "AXISBANK", "BAJFINANCE", "WIPRO", "ONGC",
    "TECHM", "MARUTI", "TITAN", "POWERGRID", "NTPC", "BAJAJFINSV", "SUNPHARMA",
    "ULTRACEMCO", "ADANIENT", "ADANIPORTS"
]

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login():
    login_url = kite.login_url()
    return redirect(login_url)

@app.route("/token")
def token():
    request_token = request.args.get("request_token")
    if not request_token:
        return "Missing request_token in URL", 400
    try:
        session_data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = session_data["access_token"]
        with open("access_token.txt", "w") as f:
            f.write(access_token)
        return redirect("/signal")
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/signal", methods=["GET", "POST"])
def signal():
    access_token = None
    try:
        with open("access_token.txt") as f:
            access_token = f.read().strip()
    except FileNotFoundError:
        return "Access token not found. Please login first via /login"

    kite.set_access_token(access_token)

    data = None
    if request.method == "POST":
        symbol = request.form["symbol"]
        try:
            quote = kite.quote(f"NSE:{symbol}")
            price = quote[f"NSE:{symbol}"]["last_price"]
            volume = quote[f"NSE:{symbol}"].get("volume_traded") or quote[f"NSE:{symbol}"].get("volume")
            signal_text = "Buy" if price % 2 == 0 else "Sell"
            data = {
                "price": f"{price:,.2f}",
                "volume": f"{volume:,}",
                "signal": signal_text
            }
        except Exception as e:
            data = {"price": "-", "volume": "-", "signal": f"Error: {str(e)}"}

    return render_template("signal.html", symbols=nse_100_symbols, data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

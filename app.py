from flask import Flask, render_template, request, redirect
from kiteconnect import KiteConnect
import os

app = Flask(__name__)

# Load Kite API key and secret from environment
api_key = os.getenv("KITE_API_KEY")
api_secret = os.getenv("KITE_API_SECRET")
access_token = os.getenv("ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
if access_token:
    kite.set_access_token(access_token)

# NSE 100 sample list (partial - add more as needed)
nse_100_symbols = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "ITC", "HINDUNILVR",
    "BHARTIARTL", "ASIANPAINT", "AXISBANK", "BAJFINANCE", "WIPRO", "ONGC", "TECHM", "MARUTI", "TITAN",
    "POWERGRID", "NTPC", "BAJAJFINSV", "SUNPHARMA", "ULTRACEMCO", "ADANIENT", "ADANIPORTS"
]

@app.route("/")
def home():
    return redirect("/signal")

# 🔵 Login URL — Redirect to Kite authorization
@app.route("/login")
def login():
    login_url = kite.login_url()
    return redirect(login_url)

# 🔵 Token capture after login
@app.route("/token")
def token():
    request_token = request.args.get("request_token")
    if request_token:
        try:
            data = kite.generate_session(request_token, api_secret=api_secret)
            access_token = data["access_token"]

            # Save token in ENV or to a secure file (optional)
            with open("access_token.txt", "w") as f:
                f.write(access_token)

            return render_template("token.html", access_token=access_token)
        except Exception as e:
            return f"Error: {e}"
    return "No request_token received."

# 🔵 Signal Logic
@app.route("/signal", methods=["GET", "POST"])
def signal():
    data = None
    if request.method == "POST":
        symbol = request.form.get("symbol")
        try:
            quote = kite.quote(f"NSE:{symbol}")
            stock = quote.get(f"NSE:{symbol}", {})
            price = stock.get("last_price", 0)
            volume = stock.get("volume_traded") or stock.get("volume") or 0
            signal_text = "Buy" if price % 2 == 0 else "Sell"

            data = {
                "price": f"{price:,.2f}",
                "volume": f"{volume:,}",
                "signal": signal_text
            }
        except Exception as e:
            data = {
                "price": "-",
                "volume": "-",
                "signal": f"Error: {str(e)}"
            }

    return render_template("signal.html", symbols=nse_100_symbols, data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

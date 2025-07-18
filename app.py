
from flask import Flask, render_template, request
from kiteconnect import KiteConnect
import os

app = Flask(__name__)

# Load access token
with open("access_token.txt", "r") as f:
    access_token = f.read().strip()

kite = KiteConnect(api_key=os.getenv("KITE_API_KEY"))
kite.set_access_token(access_token)

# Top NSE 100 symbols (sample list, extend as needed)
nse_100_symbols = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "ITC", "HINDUNILVR",
    "BHARTIARTL", "ASIANPAINT", "AXISBANK", "BAJFINANCE", "WIPRO", "ONGC", "TECHM", "MARUTI", "TITAN",
    "POWERGRID", "NTPC", "BAJAJFINSV", "SUNPHARMA", "ULTRACEMCO", "ADANIENT", "ADANIPORTS"
]

@app.route("/signal", methods=["GET", "POST"])
def signal():
    data = None
    if request.method == "POST":
        symbol = request.form["symbol"]
        try:
            quote = kite.quote(f"NSE:{symbol}")
            price = quote[f"NSE:{symbol}"]["last_price"]
            volume = quote[f"NSE:{symbol}"]["volume_traded"] or quote[f"NSE:{symbol}"]["volume"]
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

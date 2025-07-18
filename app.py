
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
    login_url = kite.login_url()
    return render_template("login.html", api_key=API_KEY, login_url=login_url)

@app.route("/token", methods=["GET", "POST"])
def token():
    access_token = None
    if request.method == "POST":
        req_token = request.form.get("request_token")
        try:
            data = kite.generate_session(req_token, api_secret=API_SECRET)
            access_token = data["access_token"]
            return render_template("token.html", access_token=access_token)
        except Exception as e:
            access_token = f"Error: {e}"
    return render_template("token.html", access_token=access_token)

@app.route("/signal")
def signal():
    try:
        access_token = os.getenv("ACCESS_TOKEN")
        if not access_token:
            return "❌ Access token missing. Set it in Render → Environment Variables as ACCESS_TOKEN."

        kite.set_access_token(access_token)
        symbol = "NSE:HDFCBANK"

        ltp_data = kite.ltp(symbol)
        ltp = ltp_data[symbol]["last_price"]
        volume = kite.quote(symbol)[symbol]["volume"]

        signal = "📈 BUY" if ltp > 1500 else "🔻 WAIT"
        return render_template("signal.html", price=ltp, volume=volume, signal=signal)

    except Exception as e:
        return f"Signal: Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route("/signal", methods=["GET", "POST"])
def signal():
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
    data = None
    if request.method == "POST":
        symbol = request.form["symbol"]
        # Dummy data logic
        data = {
            "price": "₹2,400",
            "volume": "1,200,000",
            "signal": "Buy"
        }
    return render_template("signal.html", symbols=symbols, data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

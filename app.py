from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)
API_KEY = os.getenv("COINGLASS_API_KEY")  # ← ключ будет считываться из переменной окружения

@app.route('/coinglass_price_history')
def coinglass_price_history():
    params = {
        "symbol": request.args.get("symbol"),
        "exchange": request.args.get("exchange"),
        "interval": request.args.get("interval"),
        "startTime": request.args.get("startTime"),
        "endTime": request.args.get("endTime")
    }
    headers = {"CG-API-KEY": API_KEY}
    cg_url = "https://open-api-v4.coinglass.com/api/spot/price/history"
    try:
        resp = requests.get(cg_url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # ← можно изменить порт при необходимости

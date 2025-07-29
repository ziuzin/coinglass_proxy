from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)
API_KEY = os.getenv("COINGLASS_API_KEY")
print(f"[coinglass_proxy] Loaded COINGLASS_API_KEY: {API_KEY}")

@app.route('/coinglass_price_history')
def coinglass_price_history():
    """
    Proxy the CoinGlass spot price OHLC history endpoint.
    """
    raw_params = {
        "symbol": request.args.get("symbol"),
        "exchange": request.args.get("exchange"),
        "interval": request.args.get("interval"),
        "startTime": request.args.get("startTime"),
        "endTime": request.args.get("endTime"),
    }
    # Убираем параметры со значением None или пустой строкой
    params = {k: v for k, v in raw_params.items() if v}
    if not API_KEY:
        return jsonify({"error": "Missing COINGLASS_API_KEY environment variable"}), 500
    headers = {"CG-API-KEY": API_KEY}
    cg_url = "https://open-api-v4.coinglass.com/api/spot/price/history"
    try:
        resp = requests.get(cg_url, headers=headers, params=params, timeout=10)
        # Логируем ответ для отладки
        print(f"[coinglass_proxy] Upstream status: {resp.status_code}")
        print(f"[coinglass_proxy] Upstream body: {resp.text[:500]}")
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.HTTPError as e:
        status_code = getattr(e.response, "status_code", 500)
        error_body = e.response.text if e.response else "no response body"
        print("[coinglass_proxy] API error:", e, error_body)
        return jsonify({"error": f"Upstream error: {status_code}", "detail": error_body}), 500
    except Exception as e:
        print("[coinglass_proxy] Unexpected error:", e)
        return jsonify({"error": "Unexpected server error", "detail": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

from flask import Flask, request, jsonify
import os
import requests
import json

app = Flask(__name__)

# Загружаем ключ из переменной окружения
API_KEY = os.getenv("COINGLASS_API_KEY")
print(f"[coinglass_proxy] Loaded COINGLASS_API_KEY: {API_KEY}")

@app.route('/coinglass_price_history')
def coinglass_price_history():
    """
    Проксируем эндпоинт CoinGlass /api/spot/price/history и возвращаем JSON.
    """
    raw_params = {
        "symbol": request.args.get("symbol"),
        "exchange": request.args.get("exchange"),
        "interval": request.args.get("interval"),
        "startTime": request.args.get("startTime"),
        "endTime": request.args.get("endTime"),
    }
    # Убираем ключи со значениями None/пустая строка
    params = {k: v for k, v in raw_params.items() if v}

    if not API_KEY:
        return jsonify({"error": "Missing COINGLASS_API_KEY"}), 500

    headers = {"CG-API-KEY": API_KEY}
    cg_url = "https://open-api-v4.coinglass.com/api/spot/price/history"

    try:
        resp = requests.get(cg_url, headers=headers, params=params, timeout=10)
        # Логируем код и начало тела ответа для отладки
        print(f"[coinglass_proxy] Upstream status: {resp.status_code}")
        print(f"[coinglass_proxy] Upstream body: {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()
        return jsonify(data)
    except requests.HTTPError as e:
        status_code = getattr(e.response, "status_code", 500)
        error_body = e.response.text if e.response else "no response body"
        print("[coinglass_proxy] API error:", e, error_body)
        return jsonify({
            "error": f"Upstream error: {status_code}",
            "detail": error_body
        }), 500
    except Exception as e:
        print("[coinglass_proxy] Unexpected error:", e)
        return jsonify({
            "error": "Unexpected server error",
            "detail": str(e)
        }), 500

@app.route('/coinglass_price_history_html')
def coinglass_price_history_html():
    """
    Проксируем тот же эндпоинт CoinGlass, но возвращаем результат в виде HTML.
    """
    raw_params = {
        "symbol": request.args.get("symbol"),
        "exchange": request.args.get("exchange"),
        "interval": request.args.get("interval"),
        "startTime": request.args.get("startTime"),
        "endTime": request.args.get("endTime"),
    }
    params = {k: v for k, v in raw_params.items() if v}

    if not API_KEY:
        return "<html><body><pre>Missing COINGLASS_API_KEY</pre></body></html>", 500

    headers = {"CG-API-KEY": API_KEY}
    cg_url = "https://open-api-v4.coinglass.com/api/spot/price/history"

    try:
        resp = requests.get(cg_url, headers=headers, params=params, timeout=10)
        print(f"[coinglass_proxy] Upstream status (HTML): {resp.status_code}")
        print(f"[coinglass_proxy] Upstream body (HTML): {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()
        pretty_json = json.dumps(data, indent=2)
    except requests.HTTPError as e:
        status_code = getattr(e.response, "status_code", 500)
        error_body = e.response.text if e.response else "no response body"
        print("[coinglass_proxy] API error (HTML):", e, error_body)
        return (
            "<html><body><pre>Error: Upstream error {}. Detail: {}</pre></body></html>".format(
                status_code, error_body
            ),
            500,
        )
    except Exception as e:
        print("[coinglass_proxy] Unexpected error (HTML):", e)
        return (
            "<html><body><pre>Error: {}</pre></body></html>".format(str(e)),
            500,
        )

    return "<html><body><h1>CoinGlass Response</h1><pre>{}</pre></body></html>".format(pretty_json)

if __name__ == "__main__":
    # Запускаем сервер на порту 5001
    app.run(host="0.0.0.0", port=5001)

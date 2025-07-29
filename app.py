import json

@app.route('/coinglass_price_history_html')
def coinglass_price_history_html():
    # Читаем параметры, убирая None/пустые
    raw_params = {
        "symbol": request.args.get("symbol"),
        "exchange": request.args.get("exchange"),
        "interval": request.args.get("interval"),
        "startTime": request.args.get("startTime"),
        "endTime": request.args.get("endTime"),
    }
    params = {k: v for k, v in raw_params.items() if v}

    # Проверяем наличие API-ключа
    if not API_KEY:
        return "<html><body><pre>Missing COINGLASS_API_KEY</pre></body></html>", 500

    # Делаем запрос к основному прокси
    cg_url = "https://open-api-v4.coinglass.com/api/spot/price/history"
    try:
        resp = requests.get(cg_url, headers={"CG-API-KEY": API_KEY}, params=params, timeout=10)
        data = resp.json()
    except Exception as e:
        # В случае ошибки выводим её в HTML
        return f"<html><body><pre>Error: {str(e)}</pre></body></html>", 500

    # Возвращаем HTML с JSON-ответом
    return f"<html><body><h1>CoinGlass Response</h1><pre>{json.dumps(data, indent=2)}</pre></body></html>"

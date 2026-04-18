from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

gateway = Flask(__name__)
usage_counter = {}

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/api/v1")
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "1000"))

@gateway.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    user_ip = request.remote_addr
    today = datetime.now().date()

    # Rate Limit Kontrolü
    if user_ip not in usage_counter:
        usage_counter[user_ip] = []

    # Sadece bugün yapılan istekleri filtrele
    usage_counter[user_ip] = [t for t in usage_counter[user_ip] if t.date() == today]

    if len(usage_counter[user_ip]) >= DAILY_LIMIT:
        return jsonify({
            "error": f"Rate limit exceeded. Max {DAILY_LIMIT} calls per day allowed per user."
        }), 429

    # İstek başarılı, sayacı artır
    usage_counter[user_ip].append(datetime.now())

    # İsteği gerçek API'ye yönlendir
    resp = requests.request(
        method=request.method,
        url=f"{API_URL}/{path}",
        headers={k: v for k, v in request.headers if k.lower() != 'host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        params=request.args
    )
    return (resp.content, resp.status_code, resp.headers.items())


@gateway.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "api_url": API_URL}), 200


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    gateway.run(host='0.0.0.0', port=port)

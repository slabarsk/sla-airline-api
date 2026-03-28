from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

gateway = Flask(__name__)

usage_counter = {}

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/api/v1")

@gateway.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    user_ip = request.remote_addr
    today = datetime.now().date()

    # Rate Limit Kontrolü (Günde 3 çağrı sınırı) 
    if user_ip not in usage_counter:
        usage_counter[user_ip] = []
    
    # Sadece bugün yapılan istekleri filtrele
    usage_counter[user_ip] = [t for t in usage_counter[user_ip] if t.date() == today]

    if len(usage_counter[user_ip]) >= 3:
        return jsonify({"error": "Rate limit exceeded. Max 3 calls per day allowed per user."}), 429

    # İstek başarılı, sayacı artır
    usage_counter[user_ip].append(datetime.now())

    # İsteği gerçek API'ye yönlendir (Forward)
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

if __name__ == '__main__':
    gateway.run(port=8080) # Gateway 8080 portunda çalışacak
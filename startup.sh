#!/bin/bash
set -e

echo ">>> startup.sh başladı"
echo ">>> DATABASE_URL: ${DATABASE_URL:0:50}..."
echo ">>> PORT: $PORT"

# Flask API'yi gunicorn ile başlat (background, port 5000)
echo ">>> Flask API başlatılıyor (port 5000)..."
gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 60 --access-logfile - --error-logfile - "run:app" &
API_PID=$!
echo ">>> Flask API PID: $API_PID"

# API ayaklanması için bekle ve doğrula
sleep 8
if ! kill -0 $API_PID 2>/dev/null; then
    echo "!!! Flask API crashed!"
    exit 1
fi
echo ">>> Flask API ayakta"

# Flask'a test request at
curl -s http://127.0.0.1:5000/flights/query?airport_from=ADB\&airport_to=ESB\&date_from=2026-06-20T00:00:00\&number_of_people=1 | head -c 200
echo ""

# Gateway'i foreground'da başlat (Azure $PORT'da)
export API_URL="http://127.0.0.1:5000"
GATEWAY_PORT=${PORT:-8080}
echo ">>> Gateway başlatılıyor (port $GATEWAY_PORT)..."
exec python3 gateway.py

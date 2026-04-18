#!/bin/bash
# Start Flask API in background
python3 run.py &

# Wait a moment for API to be ready
sleep 3

# Start Gateway in foreground (Azure needs at least one foreground process)
# Gateway proxies to local Flask API
export API_URL="http://127.0.0.1:5000/api/v1"
python3 gateway.py

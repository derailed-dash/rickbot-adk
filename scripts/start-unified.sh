#!/bin/bash

# Start FastAPI in the background on port 8000
echo "Starting FastAPI backend on port 8000..."
export PORT=8000
fastapi run src/main.py --port 8000 --host 0.0.0.0 &

# Wait for FastAPI to start
echo "Waiting for FastAPI to be ready..."
for i in {1..10}; do
    if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')" > /dev/null 2>&1; then
        echo "FastAPI is ready!"
        break
    fi
    echo "Waiting... ($i)"
    sleep 2
done

# Start Next.js in the foreground on port 8080
echo "Starting Next.js frontend on port 8080..."
export PORT=8080
export HOSTNAME=0.0.0.0
# Next.js will handle proxying /api to 8000 via its rewrites in next.config.js
node server.js

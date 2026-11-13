#!/data/data/com.termux/files/usr/bin/bash

SERVER_URL="http://localhost:8000/openapi.json"
STARTED_BY_SCRIPT=0

echo "=== Checking Golden-Agent Server Status ==="
if ! curl -s "$SERVER_URL" > /dev/null; then
    echo "Server not running. Starting golden_agent/monolith.py in background..."
    python golden_agent/monolith.py > server.log 2>&1 &
    SERVER_PID=$!
    STARTED_BY_SCRIPT=1

    # Wait up to 10 seconds for Uvicorn to boot
    for i in {1..10}; do
        if curl -s "$SERVER_URL" > /dev/null; then
            echo "Server is live (PID: $SERVER_PID)."
            break
        fi
        sleep 1
    done
else
    echo "Server is already running on port 8000."
fi

echo ""
echo "=== Running Pytest Verification Suite ==="
pytest -v test_suite.py

echo ""
echo "Done! Server logs are saved in ~/Golden-Agent/server.log"
if [ "$STARTED_BY_SCRIPT" -eq 1 ]; then
    echo "To stop the background server later, run: kill $SERVER_PID"
fi

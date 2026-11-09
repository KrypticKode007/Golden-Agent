#!/bin/bash
echo "Building Golden-Agent Image..."
docker build -t golden-agent:latest .
echo "Starting Golden-Agent Container..."
docker run -d -p 8000:8000 --name golden_agent_running golden-agent:latest
echo "Deployment successful. API online on port 8000."

#!/usr/bin/env bash
# ==============================================================================
# GOLDEN-AGENT SYSTEM ORGANIC PLATFORM AUTOMATED DEPLOYMENT ROUTINE
# Repository: KrypticKode007/Golden-Agent
# ==============================================================================

set -e

CLR_GOLD="\033[1;33m"
CLR_GREEN="\033[1;32m"
CLR_CYAN="\033[1;36m"
CLR_RESET="\033[0m"

echo -e "${CLR_GOLD}[1/4] Structuring local workspace directory tree topology...${CLR_RESET}"
mkdir -p golden_agent tests docs

echo -e "${CLR_GOLD}[2/4] Executing multi-tier psychological transition test suite...${CLR_RESET}"
python3 -m pytest tests/test_emotional_transitions.py -v --cov=golden_agent/

echo -e "${CLR_GOLD}[3/4] Initializing isolated Docker container compilation engine...${CLR_RESET}"
docker build -t golden-agent-organic:latest .

if [ "$(docker ps -aq -f name=golden_agent_mind_runtime)" ]; then
    echo -e "${CLR_CYAN}Clearing legacy execution container profiles...${CLR_RESET}"
    docker rm -f golden_agent_mind_runtime
fi

echo -e "${CLR_GOLD}[4/4] Deploying organic mind gateway microservice module...${CLR_RESET}"
docker run -d \
    -p 8000:8000 \
    --name golden_agent_mind_runtime \
    --restart unless-stopped \
    golden-agent-organic:latest

echo -e "${CLR_GREEN}==========================================================================${CLR_RESET}"
echo -e "${CLR_GREEN}⚡ ARCHITECTURE SECURED: ALL GRIDS BYPASSED & NARRATIVE LEDGER ONLINE ⚡${CLR_RESET}"
echo -e "${CLR_GREEN}==========================================================================${CLR_RESET}"
echo -e " -> Live Mind State URL : http://localhost:8000/mind/state"
echo -e " -> Reflection Endpoint : http://localhost:8000/mind/reflect"
echo -e " -> Text Journal View   : http://localhost:8000/mind/journal"
echo -e " -> Operating Standard  : 100% Unstructured Experiential Streaming Active"
echo -e "${CLR_GREEN}==========================================================================${CLR_RESET}"

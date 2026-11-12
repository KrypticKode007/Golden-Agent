# Multi-stage Dockerfile for Project Kai-007: Unified Golden-Agent Monolith
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Create non-root user for isolated execution
RUN useradd -m -u 1000 kai_agent && chown -R kai_agent:kai_agent /app

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

COPY unified_monolith.py ./golden_agent/unified_monolith.py
COPY test_unified_monolith.py ./tests/test_unified_monolith.py

RUN mkdir -p /app/data && chown -R kai_agent:kai_agent /app/data
USER kai_agent

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/audit')" || exit 1

CMD ["uvicorn", "golden_agent.unified_monolith:app", "--host", "0.0.0.0", "--port", "8000"]

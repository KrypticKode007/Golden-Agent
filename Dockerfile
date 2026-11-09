# ==========================================
# Stage 1: Build compilation and setup
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN echo "fastapi==0.110.0\nuvicorn==0.28.0\npydantic==2.6.4\npytest==8.1.1\npytest-cov==4.1.0" > requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# ==========================================
# Stage 2: Final safe production execution
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

mkdir -p golden_agent tests

COPY golden_agent/ ./golden_agent/

EXPOSE 8000

# Clamp execution permissions using non-root container profile tags
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "golden_agent.monolith:app", "--host", "0.0.0.0", "--port", "8000"]

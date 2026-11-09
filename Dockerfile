FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN echo "fastapi==0.110.0\nuvicorn==0.28.0\npydantic==2.6.4\npytest==8.1.1" > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

mkdir -p golden_agent tests

COPY golden_agent/ ./golden_agent/

EXPOSE 8000

RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python3", "golden_agent/status_listener.py"]

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY golden_agent/ ./golden_agent/
COPY tests/ ./tests/
EXPOSE 8000
CMD ["uvicorn", "golden_agent.server:app", "--host", "0.0.0.0", "--port", "8000"]

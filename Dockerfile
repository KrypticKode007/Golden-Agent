# Python 3.12 slim Dockerfile setup for Golden-Agent
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY profiles/ ./profiles/
COPY examples/ ./examples/
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "golden_agent.interfaces.api:app", "--host", "0.0.0.0", "--port", "8000"]

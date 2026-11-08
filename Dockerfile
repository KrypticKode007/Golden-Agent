FROM python:3.10-slim
RUN apt-get update && apt-get install -y g++ cmake sqlite3 libsqlite3-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir psutil numpy websockets requests
CMD ["python3", "main_sentience_core (2).py"]

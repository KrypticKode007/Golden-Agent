# Base environment using optimized minimal Python footprint
FROM python:3.10-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install basic toolchains required for C++ native compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    make \
    sqlite3 \
    libsqlite3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up runtime application tree
WORKDIR /app

# Copy dependency records first to optimize container caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy active repository assets
COPY . /app/

# Build native performance libraries inside container space
RUN if [ -f "kryptic_hardware_accelerator.cpp" ]; then \
        g++ -O3 -shared -fPIC kryptic_hardware_accelerator.cpp -o libkryptic_core.so; \
    fi

# Set executable flags for pipeline scripts
RUN chmod +x run_pipeline.sh

# Bootstrap the automated pipeline directly upon image activation
CMD ["./run_pipeline.sh"]

# ==============================================================================
# STAGE 1: Build high-speed C++ native acceleration binaries
# ==============================================================================
FROM ubuntu:22.04 AS cpp-builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    make \
    cmake \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY kryptic_hardware_accelerator.cpp .

# Compile using strict production optimization flags
RUN g++ -O3 -std=c++17 -Wall -Wextra -Werror kryptic_hardware_accelerator.cpp -o matrix_accelerator \
    && chmod +x matrix_accelerator

# ==============================================================================
# STAGE 2: Final runtime environment with correct module paths
# ==============================================================================
FROM python:3.10-slim AS runtime

# Align PYTHONPATH context across modules
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:${PYTHONPATH:-}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the native accelerator from Stage 1
COPY --from=cpp-builder /build/matrix_accelerator /app/matrix_accelerator

# Copy remaining framework source files
COPY . /app/

EXPOSE 8000

CMD ["python", "kryptic_edge_launch.py"]

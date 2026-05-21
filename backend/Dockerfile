FROM python:3.12-slim AS builder

WORKDIR /app

# Install build-time deps only in the builder stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.lock ./
ENV PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org pypi.python.org"
RUN pip install --no-cache-dir --prefix=/install -r requirements.lock

# ---- Final stage ----
FROM python:3.12-slim

WORKDIR /app

# Only runtime lib needed (libpq for asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder (no gcc, no build tools)
COPY --from=builder /install /usr/local

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

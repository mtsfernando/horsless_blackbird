FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements.lock ./
ENV PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org pypi.python.org"
RUN pip install --no-cache-dir -r requirements.lock

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Copy source code
COPY src/ ./src/

# Default command (run scraper)
CMD ["python", "-m", "src.scrape"]

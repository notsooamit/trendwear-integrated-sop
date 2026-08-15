FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (Cbc solver tools if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    coinor-cbc \
    coinor-libcbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Environment variable for port
ENV PORT=8000
EXPOSE 8000

# Start server
CMD ["python", "-m", "server.http_server"]

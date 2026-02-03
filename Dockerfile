FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for crypto libraries
RUN apt-get update && apt-get install -y \
    gcc \
    libgmp-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY bot.py .

CMD ["python", "bot.py"]

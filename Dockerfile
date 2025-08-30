# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and tests
COPY app/ ./app/
COPY tests/ ./tests/
COPY pytest.ini ./

# Create non-root user and set up directories
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser ./tests && \
    chown appuser:appuser ./pytest.ini && \
    mkdir -p /home/appuser/.cache && \
    chown -R appuser:appuser /home/appuser/.cache

USER appuser

# Create Hugging Face cache directory with correct permissions
RUN mkdir -p /home/appuser/.cache/huggingface

# Expose port
EXPOSE 8000



# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
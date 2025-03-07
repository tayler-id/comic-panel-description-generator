FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Create uploads directory
RUN mkdir -p uploads && \
    chmod 777 uploads

# Run as non-root user for better security
RUN useradd -m appuser
USER appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    # Default to empty values for API keys, will be overridden at runtime
    OPENAI_API_KEY="" \
    ANTHROPIC_API_KEY="" \
    GROK_API_KEY="" \
    DEEPSEEK_API_KEY="" \
    GOOGLE_API_KEY="" \
    HUGGINGFACE_API_KEY="" \
    BRAVE_API_KEY=""

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application with increased timeout
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "60", "app:app"]

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
COPY mcp_server/requirements.txt ./mcp_requirements.txt

# Install Python dependencies
# Note: We've commented out the mcp package in requirements.txt and mcp_requirements.txt
# as it's not available on PyPI and is only needed for Claude integration
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r mcp_requirements.txt || echo "Warning: Some MCP dependencies could not be installed. MCP server functionality will be disabled."

# Copy application code
COPY app/ ./app/
COPY mcp_server/ ./mcp_server/

# Create uploads directory
RUN mkdir -p app/uploads && \
    chmod 777 app/uploads

# Run as non-root user for better security
RUN useradd -m appuser
USER appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    API_PORT=8001 \
    # MCP configuration
    MCP_SERVER_NAME="comic-panel" \
    USE_MCP="false" \
    # Default to empty values for API keys, will be overridden at runtime
    OPENAI_API_KEY="" \
    ANTHROPIC_API_KEY="" \
    GROK_API_KEY="" \
    DEEPSEEK_API_KEY="" \
    GOOGLE_API_KEY="" \
    HUGGINGFACE_API_KEY="" \
    BRAVE_API_KEY=""

# Expose the ports
EXPOSE 8000
EXPOSE 8001

# Command to run the application with increased timeout
# We use a shell to allow for environment variable expansion
CMD ["sh", "-c", "python -m app.api_server & gunicorn --bind 0.0.0.0:${PORT} --timeout 60 --pythonpath app app:app"]

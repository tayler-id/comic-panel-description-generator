#!/bin/bash

# Script to run the Docker container with environment variables from .env file

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    exit 1
fi

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Build the Docker image
echo "Building Docker image..."
docker build -t comic-panel-description-generator .

# Run the Docker container with environment variables
echo "Running Docker container..."
docker run -p 8000:8000 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    -e GROK_API_KEY="$GROK_API_KEY" \
    -e DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
    -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
    -e HUGGINGFACE_API_KEY="$HUGGINGFACE_API_KEY" \
    -e BRAVE_API_KEY="$BRAVE_API_KEY" \
    comic-panel-description-generator

# Unset environment variables
unset OPENAI_API_KEY ANTHROPIC_API_KEY GROK_API_KEY DEEPSEEK_API_KEY GOOGLE_API_KEY HUGGINGFACE_API_KEY BRAVE_API_KEY

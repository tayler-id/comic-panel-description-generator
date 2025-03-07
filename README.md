# Comic Panel Description Generator

An AI-powered tool that automatically converts comic sketches into textual panel descriptions, saving comic artists hours of tedious scripting work.

## Features

- Upload comic sketches (JPG/PNG)
- Automatic panel analysis using computer vision
- AI-generated descriptions for each panel
- Simple, fast web interface
- Docker containerized for easy deployment

## Tech Stack

- Python 3.9
- OpenCV for image processing
- Flask for web interface
- Transformers/Grok API for text generation
- Docker for containerization
- Deployed on Render.com

## Quick Start

### API Keys Setup

The application uses multiple AI providers for text generation. Create a `.env` file in the root directory with your API keys:

```
# API Keys for Comic Panel Description Generator
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GROK_API_KEY=your_grok_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
GOOGLE_API_KEY=your_google_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
BRAVE_API_KEY=your_brave_api_key
```

The application will use these APIs in order of priority, falling back to the next one if any fails.

### Running Locally with Docker

#### Using the Convenience Scripts

On Windows:
```powershell
# Run the PowerShell script
.\run_docker.ps1
```

On Linux/Mac:
```bash
# Make the script executable (first time only)
chmod +x run_docker.sh

# Run the shell script
./run_docker.sh
```

These scripts will automatically load the API keys from your `.env` file and pass them to the Docker container.

#### Manual Docker Commands

```bash
# Build the Docker image
docker build -t comic-panel-generator .

# Run the container with environment variables
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your_openai_api_key" \
  -e ANTHROPIC_API_KEY="your_anthropic_api_key" \
  -e GROK_API_KEY="your_grok_api_key" \
  -e DEEPSEEK_API_KEY="your_deepseek_api_key" \
  -e GOOGLE_API_KEY="your_google_api_key" \
  -e HUGGINGFACE_API_KEY="your_huggingface_api_key" \
  -e BRAVE_API_KEY="your_brave_api_key" \
  comic-panel-generator
```

Then visit http://localhost:8000 in your browser.

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys (see above)

# Run development server
flask run --debug
```

## Usage

1. Upload your comic sketch through the web interface
2. Wait a few seconds for processing
3. View the generated panel descriptions
4. Copy or download the results

## Project Structure

```
/
  ├── .env             # Environment variables (API keys)
  ├── run_docker.sh    # Shell script to run Docker with env vars
  ├── run_docker.ps1   # PowerShell script to run Docker with env vars
  ├── requirements.txt # Python dependencies
  ├── Dockerfile       # Docker configuration
  └── app/
      ├── app.py       # Flask application
      ├── vision.py    # OpenCV image processing
      ├── textgen.py   # Multi-API text generation
      ├── static/      # CSS, JS, and static assets
      ├── templates/   # HTML templates
      └── uploads/     # Temporary storage for uploads
```

## License

MIT

## Pricing

- Subscription: $20/month for unlimited use
- One-time Purchase: $50 for perpetual license

Contact us for more information!

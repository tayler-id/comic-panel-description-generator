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

### Running Locally with Docker

```bash
# Build the Docker image
docker build -t comic-panel-generator .

# Run the container
docker run -p 8000:8000 comic-panel-generator
```

Then visit http://localhost:8000 in your browser.

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

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
/app
  ├── app.py           # Flask application
  ├── vision.py        # OpenCV image processing
  ├── textgen.py       # Text generation (Grok/GPT-2)
  ├── static/          # CSS, JS, and static assets
  ├── templates/       # HTML templates
  └── uploads/         # Temporary storage for uploads
```

## License

MIT

## Pricing

- Subscription: $20/month for unlimited use
- One-time Purchase: $50 for perpetual license

Contact us for more information!

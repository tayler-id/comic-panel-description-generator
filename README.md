# Comic Panel Description Generator

An AI-powered tool that automatically converts comic sketches into textual panel descriptions, saving comic artists hours of tedious scripting work.

## Features

- Upload comic sketches (JPG/PNG)
- Automatic panel analysis using computer vision
- AI-generated descriptions for each panel
- Simple, fast web interface
- Docker containerized for easy deployment
- API-only mode for integration with other applications
- MCP (Model Context Protocol) server for Claude integration

## Tech Stack

- Python 3.9
- OpenCV for image processing
- Flask for web interface and API
- Transformers/Grok API for text generation
- MCP server for Claude integration
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

## API Usage

The application provides a REST API for integration with other applications:

### Analyze a Comic Panel

```
POST /api/analyze
Content-Type: application/json

{
  "image_data": "base64_encoded_image_data",
  "is_path": false,
  "panel_num": 1
}
```

Response:
```json
{
  "figures": 2,
  "motion": "action",
  "objects": "sparks"
}
```

### Generate a Description

```
POST /api/describe
Content-Type: application/json

{
  "image_data": {
    "figures": 2,
    "motion": "action",
    "objects": "sparks"
  },
  "panel_num": 1
}
```

Response:
```json
{
  "description": "Panel 1: Two characters in a dynamic scene with visual effects like sparks or impact lines. The characters appear to be engaged in combat."
}
```

## MCP Server

The application includes an MCP (Model Context Protocol) server that can be used with Claude to analyze comic panels and generate descriptions.

### Adding the MCP Server to Claude

We provide convenience scripts to add the MCP server to Claude's settings:

#### Windows:
```powershell
# Run the PowerShell script
.\add_mcp_server.ps1
```

#### Linux/Mac:
```bash
# Make the script executable (first time only)
chmod +x add_mcp_server.sh

# Run the shell script
./add_mcp_server.sh
```

These scripts will:
1. Add the Comic Panel MCP server to Claude's MCP settings
2. Prompt you to enter your API keys
3. Provide example usage instructions

### Manual Setup

If you prefer to set up the MCP server manually:

1. Add the server to your Claude MCP settings:

```json
{
  "mcpServers": {
    "comic-panel": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "OPENAI_API_KEY": "your_openai_api_key"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

2. Use the tools in Claude:

```
<use_mcp_tool>
<server_name>comic-panel</server_name>
<tool_name>analyze_panel</tool_name>
<arguments>
{
  "image_data": "/path/to/comic_panel.jpg",
  "panel_num": 1,
  "is_path": true
}
</arguments>
</use_mcp_tool>
```

## Project Structure

```
/
  ├── .env             # Environment variables (API keys)
  ├── run_docker.sh    # Shell script to run Docker with env vars
  ├── run_docker.ps1   # PowerShell script to run Docker with env vars
  ├── add_mcp_server.sh # Shell script to add MCP server to Claude
  ├── add_mcp_server.ps1 # PowerShell script to add MCP server to Claude
  ├── requirements.txt # Python dependencies
  ├── Dockerfile       # Docker configuration
  ├── render.yaml      # Render.com deployment configuration
  ├── app/
  │   ├── app.py       # Flask application
  │   ├── api_server.py # API server
  │   ├── mcp_client.py # MCP client
  │   ├── vision.py    # OpenCV image processing
  │   ├── textgen.py   # Multi-API text generation
  │   ├── static/      # CSS, JS, and static assets
  │   ├── templates/   # HTML templates
  │   └── uploads/     # Temporary storage for uploads
  └── mcp_server/      # MCP server for Claude integration
      ├── server.py    # Main MCP server
      ├── tools/       # MCP tools
      │   ├── detect_objects.py      # Object detection tool
      │   ├── classify_scene.py      # Scene classification tool
      │   ├── analyze_relationships.py # Relationship analysis tool
      │   ├── generate_description.py # Description generation tool
      │   └── analyze_panel.py       # Complete panel analysis tool
      └── utils/       # Utility functions
          ├── image_utils.py         # Image processing utilities
          └── api_utils.py           # API utilities
```

## License

MIT

## Pricing

- Subscription: $20/month for unlimited use
- One-time Purchase: $50 for perpetual license

Contact us for more information!

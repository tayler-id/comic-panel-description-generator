# Comic Panel MCP Server

A Model Context Protocol (MCP) server for analyzing comic panels and generating accurate descriptions.

## Features

- **Object Detection**: Detect characters and objects in comic panels
- **Scene Classification**: Classify the scene type and attributes
- **Relationship Analysis**: Analyze spatial relationships between characters
- **Description Generation**: Generate accurate panel descriptions based on analysis
- **Complete Panel Analysis**: All-in-one analysis pipeline

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables for API keys (optional but recommended):

```bash
# For OpenAI API (improves description quality)
export OPENAI_API_KEY=your_openai_api_key

# For Anthropic API (alternative provider)
export ANTHROPIC_API_KEY=your_anthropic_api_key

# For Grok API (alternative provider)
export GROK_API_KEY=your_grok_api_key

# For DeepSeek API (alternative provider)
export DEEPSEEK_API_KEY=your_deepseek_api_key
```

## Usage

### Running the Server

```bash
python -m mcp_server.server
```

### Using with Claude

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

## Available Tools

### detect_objects

Detects characters and objects in a comic panel image.

```json
{
  "image_data": "path/to/image.jpg",
  "is_path": true
}
```

### classify_scene

Classifies the scene type in a comic panel.

```json
{
  "image_data": "path/to/image.jpg",
  "is_path": true
}
```

### analyze_relationships

Analyzes relationships between characters in a comic panel.

```json
{
  "image_data": "path/to/image.jpg",
  "figures": [...],
  "is_path": true
}
```

### generate_description

Generates a description for a comic panel based on analysis.

```json
{
  "panel_num": 1,
  "figures": [...],
  "scene_type": "action",
  "attributes": ["dynamic", "bright"],
  "relationships": [...]
}
```

### analyze_panel

Complete analysis of a comic panel (all steps in one).

```json
{
  "image_data": "path/to/image.jpg",
  "panel_num": 1,
  "is_path": true
}
```

## License

MIT

i#!/bin/bash

# Shell script to add the Comic Panel MCP server to Claude's MCP settings

# Define the path to the Claude MCP settings file
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    SETTINGS_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
else
    # Linux
    SETTINGS_PATH="$HOME/.config/Claude/claude_desktop_config.json"
fi

# Check if the settings file exists
if [ ! -f "$SETTINGS_PATH" ]; then
    echo "Claude MCP settings file not found at: $SETTINGS_PATH"
    echo "Please make sure Claude is installed and has been run at least once."
    exit 1
fi

# Read the current settings
if ! SETTINGS=$(cat "$SETTINGS_PATH"); then
    echo "Error reading settings file"
    exit 1
fi

# Get the current directory for the MCP server
CURRENT_DIR=$(pwd)
SERVER_PATH="$CURRENT_DIR/mcp_server/server.py"

# Check if the mcpServers property exists and create it if it doesn't
if ! echo "$SETTINGS" | grep -q '"mcpServers"'; then
    # Add mcpServers property
    SETTINGS=$(echo "$SETTINGS" | sed 's/}/,"mcpServers":{}}/')
fi

# Create the Comic Panel MCP server configuration
SERVER_CONFIG='{
  "command": "python",
  "args": ["-m", "mcp_server.server"],
  "env": {
    "OPENAI_API_KEY": "",
    "ANTHROPIC_API_KEY": "",
    "GROK_API_KEY": "",
    "DEEPSEEK_API_KEY": ""
  },
  "disabled": false,
  "autoApprove": []
}'

# Add or update the Comic Panel MCP server
# This is a bit tricky with just shell tools, so we'll use a temporary file
TMP_FILE=$(mktemp)
echo "$SETTINGS" > "$TMP_FILE"

# Use jq if available, otherwise use a simple sed replacement
if command -v jq &> /dev/null; then
    jq --argjson server "$SERVER_CONFIG" '.mcpServers."comic-panel" = $server' "$TMP_FILE" > "$TMP_FILE.new"
    mv "$TMP_FILE.new" "$TMP_FILE"
else
    # Simple sed replacement - this is a fallback and might not work in all cases
    if grep -q '"comic-panel"' "$TMP_FILE"; then
        # Update existing server
        sed -i.bak 's/"comic-panel":{[^}]*}/"comic-panel":'"$SERVER_CONFIG"'/g' "$TMP_FILE"
    else
        # Add new server
        sed -i.bak 's/"mcpServers":{/"mcpServers":{"comic-panel":'"$SERVER_CONFIG"',/g' "$TMP_FILE"
    fi
fi

# Save the updated settings
if ! cp "$TMP_FILE" "$SETTINGS_PATH"; then
    echo "Error saving settings file"
    rm "$TMP_FILE"
    exit 1
fi

rm "$TMP_FILE"
echo "Successfully added Comic Panel MCP server to Claude's MCP settings."
echo "You can now use the MCP server with Claude."

# Prompt the user to add API keys
echo ""
echo "To use the MCP server with Claude, you need to add your API keys to the settings file."
echo "You can do this manually by editing the file at: $SETTINGS_PATH"
echo "Or you can provide them now:"

read -p "Enter your OpenAI API key (leave blank to skip): " OPENAI_KEY
read -p "Enter your Anthropic API key (leave blank to skip): " ANTHROPIC_KEY
read -p "Enter your Grok API key (leave blank to skip): " GROK_KEY
read -p "Enter your DeepSeek API key (leave blank to skip): " DEEPSEEK_KEY

# Update the settings with the provided API keys
if [ -n "$OPENAI_KEY" ] || [ -n "$ANTHROPIC_KEY" ] || [ -n "$GROK_KEY" ] || [ -n "$DEEPSEEK_KEY" ]; then
    TMP_FILE=$(mktemp)
    cat "$SETTINGS_PATH" > "$TMP_FILE"
    
    if command -v jq &> /dev/null; then
        # Use jq for updating keys
        if [ -n "$OPENAI_KEY" ]; then
            jq --arg key "$OPENAI_KEY" '.mcpServers."comic-panel".env.OPENAI_API_KEY = $key' "$TMP_FILE" > "$TMP_FILE.new"
            mv "$TMP_FILE.new" "$TMP_FILE"
        fi
        
        if [ -n "$ANTHROPIC_KEY" ]; then
            jq --arg key "$ANTHROPIC_KEY" '.mcpServers."comic-panel".env.ANTHROPIC_API_KEY = $key' "$TMP_FILE" > "$TMP_FILE.new"
            mv "$TMP_FILE.new" "$TMP_FILE"
        fi
        
        if [ -n "$GROK_KEY" ]; then
            jq --arg key "$GROK_KEY" '.mcpServers."comic-panel".env.GROK_API_KEY = $key' "$TMP_FILE" > "$TMP_FILE.new"
            mv "$TMP_FILE.new" "$TMP_FILE"
        fi
        
        if [ -n "$DEEPSEEK_KEY" ]; then
            jq --arg key "$DEEPSEEK_KEY" '.mcpServers."comic-panel".env.DEEPSEEK_API_KEY = $key' "$TMP_FILE" > "$TMP_FILE.new"
            mv "$TMP_FILE.new" "$TMP_FILE"
        fi
    else
        # Simple sed replacement - this is a fallback and might not work in all cases
        if [ -n "$OPENAI_KEY" ]; then
            sed -i.bak 's/"OPENAI_API_KEY":"[^"]*"/"OPENAI_API_KEY":"'"$OPENAI_KEY"'"/g' "$TMP_FILE"
        fi
        
        if [ -n "$ANTHROPIC_KEY" ]; then
            sed -i.bak 's/"ANTHROPIC_API_KEY":"[^"]*"/"ANTHROPIC_API_KEY":"'"$ANTHROPIC_KEY"'"/g' "$TMP_FILE"
        fi
        
        if [ -n "$GROK_KEY" ]; then
            sed -i.bak 's/"GROK_API_KEY":"[^"]*"/"GROK_API_KEY":"'"$GROK_KEY"'"/g' "$TMP_FILE"
        fi
        
        if [ -n "$DEEPSEEK_KEY" ]; then
            sed -i.bak 's/"DEEPSEEK_API_KEY":"[^"]*"/"DEEPSEEK_API_KEY":"'"$DEEPSEEK_KEY"'"/g' "$TMP_FILE"
        fi
    fi
    
    # Save the updated settings
    if ! cp "$TMP_FILE" "$SETTINGS_PATH"; then
        echo "Error updating API keys"
        rm "$TMP_FILE"
        exit 1
    fi
    
    rm "$TMP_FILE"
    echo "API keys have been updated."
fi

echo ""
echo "Setup complete! You can now use the Comic Panel MCP server with Claude."
echo "Example usage:"
echo ""
echo "<use_mcp_tool>"
echo "<server_name>comic-panel</server_name>"
echo "<tool_name>analyze_panel</tool_name>"
echo "<arguments>"
echo "{"
echo "  \"image_data\": \"/path/to/comic_panel.jpg\","
echo "  \"panel_num\": 1,"
echo "  \"is_path\": true"
echo "}"
echo "</arguments>"
echo "</use_mcp_tool>"

# PowerShell script to add the Comic Panel MCP server to Claude's MCP settings

# Define the path to the Claude MCP settings file
$settingsPath = "$env:APPDATA\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json"

# Check if the settings file exists
if (-not (Test-Path $settingsPath)) {
    Write-Host "Claude MCP settings file not found at: $settingsPath"
    Write-Host "Please make sure Claude is installed and has been run at least once."
    exit 1
}

# Read the current settings
try {
    $settings = Get-Content -Path $settingsPath -Raw | ConvertFrom-Json
} catch {
    Write-Host "Error reading settings file: $_"
    exit 1
}

# Get the current directory for the MCP server
$currentDir = Get-Location
$serverPath = Join-Path $currentDir "mcp_server\server.py"

# Check if the mcpServers property exists
if (-not (Get-Member -InputObject $settings -Name "mcpServers" -MemberType Properties)) {
    # Create the mcpServers property if it doesn't exist
    $settings | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value @{}
}

# Add or update the Comic Panel MCP server
$settings.mcpServers | Add-Member -MemberType NoteProperty -Name "comic-panel" -Value @{
    "command" = "python"
    "args" = @("-m", "mcp_server.server")
    "env" = @{
        "OPENAI_API_KEY" = ""
        "ANTHROPIC_API_KEY" = ""
        "GROK_API_KEY" = ""
        "DEEPSEEK_API_KEY" = ""
    }
    "disabled" = $false
    "autoApprove" = @()
} -Force

# Save the updated settings
try {
    $settings | ConvertTo-Json -Depth 10 | Set-Content -Path $settingsPath
    Write-Host "Successfully added Comic Panel MCP server to Claude's MCP settings."
    Write-Host "You can now use the MCP server with Claude."
} catch {
    Write-Host "Error saving settings file: $_"
    exit 1
}

# Prompt the user to add API keys
Write-Host ""
Write-Host "To use the MCP server with Claude, you need to add your API keys to the settings file."
Write-Host "You can do this manually by editing the file at: $settingsPath"
Write-Host "Or you can provide them now:"

$openaiKey = Read-Host "Enter your OpenAI API key (leave blank to skip)"
$anthropicKey = Read-Host "Enter your Anthropic API key (leave blank to skip)"
$grokKey = Read-Host "Enter your Grok API key (leave blank to skip)"
$deepseekKey = Read-Host "Enter your DeepSeek API key (leave blank to skip)"

# Update the settings with the provided API keys
try {
    $settings = Get-Content -Path $settingsPath -Raw | ConvertFrom-Json
    
    if ($openaiKey) {
        $settings.mcpServers."comic-panel".env.OPENAI_API_KEY = $openaiKey
    }
    
    if ($anthropicKey) {
        $settings.mcpServers."comic-panel".env.ANTHROPIC_API_KEY = $anthropicKey
    }
    
    if ($grokKey) {
        $settings.mcpServers."comic-panel".env.GROK_API_KEY = $grokKey
    }
    
    if ($deepseekKey) {
        $settings.mcpServers."comic-panel".env.DEEPSEEK_API_KEY = $deepseekKey
    }
    
    $settings | ConvertTo-Json -Depth 10 | Set-Content -Path $settingsPath
    Write-Host "API keys have been updated."
} catch {
    Write-Host "Error updating API keys: $_"
    exit 1
}

Write-Host ""
Write-Host "Setup complete! You can now use the Comic Panel MCP server with Claude."
Write-Host "Example usage:"
Write-Host ""
Write-Host "<use_mcp_tool>"
Write-Host "<server_name>comic-panel</server_name>"
Write-Host "<tool_name>analyze_panel</tool_name>"
Write-Host "<arguments>"
Write-Host "{"
Write-Host "  \"image_data\": \"/path/to/comic_panel.jpg\","
Write-Host "  \"panel_num\": 1,"
Write-Host "  \"is_path\": true"
Write-Host "}"
Write-Host "</arguments>"
Write-Host "</use_mcp_tool>"

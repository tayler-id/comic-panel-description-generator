# PowerShell script to run the Docker container with environment variables from .env file

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Error "Error: .env file not found!"
    exit 1
}

# Load environment variables from .env file
$envVars = Get-Content .env | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
    $key, $value = $_ -split '=', 2
    [PSCustomObject]@{
        Key = $key.Trim()
        Value = $value.Trim()
    }
}

# Build the Docker image
Write-Host "Building Docker image..."
docker build -t comic-panel-description-generator .

# Prepare environment variables for Docker run command
$envParams = @()
foreach ($var in $envVars) {
    if ($var.Key -and $var.Value) {
        $envParams += "-e"
        $envParams += "$($var.Key)=$($var.Value)"
    }
}

# Run the Docker container with environment variables
Write-Host "Running Docker container..."
$runParams = @(
    "run",
    "-p", "8000:8000"
)
$runParams += $envParams
$runParams += "comic-panel-description-generator"

docker $runParams

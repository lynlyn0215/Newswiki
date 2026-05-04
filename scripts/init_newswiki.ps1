param(
  [Parameter(Mandatory = $true)]
  [string]$Target
)

$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$targetPath = Resolve-Path -LiteralPath (New-Item -ItemType Directory -Path $Target -Force)

$dirs = @(
  "data/news",
  "inbox",
  "logs",
  "outputs",
  "reports",
  "state",
  "wiki",
  "raw",
  "reviews",
  "config",
  "agents"
)

foreach ($dir in $dirs) {
  New-Item -ItemType Directory -Path (Join-Path $targetPath $dir) -Force | Out-Null
}

Copy-Item -Path (Join-Path $repo "templates/wiki/wiki/*") -Destination (Join-Path $targetPath "wiki") -Recurse -Force
Copy-Item -Path (Join-Path $repo "templates/wiki/AGENTS.md") -Destination (Join-Path $targetPath "AGENTS.md") -Force
Copy-Item -Path (Join-Path $repo "templates/config/*.yaml") -Destination (Join-Path $targetPath "config") -Force
Copy-Item -Path (Join-Path $repo "templates/config/mcp.example.toml") -Destination (Join-Path $targetPath "config/mcp.example.toml") -Force
Copy-Item -Path (Join-Path $repo "templates/agents/startup-protocol.md") -Destination (Join-Path $targetPath "agents/startup-protocol.md") -Force
Copy-Item -Path (Join-Path $repo "examples/capabilities.example.json") -Destination (Join-Path $targetPath "capabilities.json") -Force
Copy-Item -Path (Join-Path $repo "examples/news/*.json") -Destination (Join-Path $targetPath "data/news") -Force

$scanner = Join-Path $repo "scripts/build_capabilities.py"
if (Get-Command python -ErrorAction SilentlyContinue) {
  python $scanner --output (Join-Path $targetPath "capabilities.json") | Out-Null
}

@"
# Private Newswiki Instance

This directory is private by default.

Start:

1. Edit config/sources.example.yaml.
2. Edit config/pipeline.example.yaml.
3. Refresh capabilities when your local tools change:
   python "$repo\scripts\build_capabilities.py" --output "$targetPath\capabilities.json"
4. Configure the three MCPs from config/mcp.example.toml.
5. Ask your agent to follow AGENTS.md.
"@ | Set-Content -Path (Join-Path $targetPath "README.md") -Encoding UTF8

Write-Output "Created private Newswiki instance at $targetPath"

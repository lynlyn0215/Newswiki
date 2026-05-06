param(
  [Parameter(Mandatory = $true)]
  [string]$Target,

  [switch]$SkipInstall,
  [switch]$SkipCapabilityScan,
  [switch]$SkipHostedSmoke
)

$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

$repo = Split-Path -Parent $PSScriptRoot
$targetPath = (New-Item -ItemType Directory -Path $Target -Force).FullName
$report = [ordered]@{
  ok = $true
  repo = $repo
  private_instance = $targetPath
  steps = @()
}

function Add-Step {
  param(
    [string]$Name,
    [bool]$Ok,
    [string]$Detail = ""
  )
  $script:report.steps += [ordered]@{
    name = $Name
    ok = $Ok
    detail = $Detail
  }
  if (-not $Ok) {
    $script:report.ok = $false
  }
}

function Run-Step {
  param(
    [string]$Name,
    [scriptblock]$Action
  )
  $previousErrorActionPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    $global:LASTEXITCODE = 0
    $output = & $Action 2>&1 | Out-String
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference
    if ($exitCode -ne 0) {
      throw "Command exited with code $exitCode. $($output.Trim())"
    }
    Add-Step -Name $Name -Ok $true -Detail $output.Trim()
  } catch {
    $ErrorActionPreference = $previousErrorActionPreference
    Add-Step -Name $Name -Ok $false -Detail $_.Exception.Message
    throw
  }
}

if (-not $SkipInstall) {
  Run-Step -Name "install dependencies" -Action {
    python -m pip install -r (Join-Path $repo "requirements.txt")
  }
} else {
  Add-Step -Name "install dependencies" -Ok $true -Detail "skipped"
}

Run-Step -Name "initialize private instance" -Action {
  powershell -ExecutionPolicy Bypass -File (Join-Path $repo "scripts/init_newswiki.ps1") -Target $targetPath
}

if (-not $SkipCapabilityScan) {
  Run-Step -Name "build capability catalog" -Action {
    python (Join-Path $repo "scripts/build_capabilities.py") --output (Join-Path $targetPath "capabilities.json")
  }
} else {
  Add-Step -Name "build capability catalog" -Ok $true -Detail "skipped"
}

Run-Step -Name "validate public export examples" -Action {
  python (Join-Path $repo "scripts/validate_public_export.py") (Join-Path $repo "examples/public")
}

Run-Step -Name "privacy scan public template" -Action {
  python (Join-Path $repo "scripts/privacy_scan.py")
}

if (-not $SkipHostedSmoke) {
  Run-Step -Name "hosted MCP smoke" -Action {
    $stderrPath = Join-Path ([System.IO.Path]::GetTempPath()) ("newswiki-mcp-smoke-" + [guid]::NewGuid().ToString("N") + ".log")
    python (Join-Path $repo "scripts/smoke_mcp_client.py") --api-key local-key --export-dir (Join-Path $repo "examples/public") 2>$stderrPath
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
      Get-Content -LiteralPath $stderrPath
      exit $exitCode
    }
    Remove-Item -LiteralPath $stderrPath -Force
  }
} else {
  Add-Step -Name "hosted MCP smoke" -Ok $true -Detail "skipped"
}

$reportPath = Join-Path $targetPath "setup-report.json"
$report | ConvertTo-Json -Depth 6 | Set-Content -Path $reportPath -Encoding UTF8

Write-Output "Newswiki agent setup complete."
Write-Output "Private instance: $targetPath"
Write-Output "Setup report: $reportPath"

if (-not $report.ok) {
  exit 1
}

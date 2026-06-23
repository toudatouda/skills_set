param(
  [switch]$DryRun,
  [switch]$List
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$Dest = Join-Path $CodexHome "skills"

$Skills = Get-ChildItem -LiteralPath $Root -Directory |
  Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") } |
  Sort-Object Name

if (-not $Skills) {
  throw "No skill directories found under $Root"
}

if ($List) {
  $Skills | ForEach-Object { $_.Name }
  exit 0
}

if (-not $DryRun) {
  New-Item -ItemType Directory -Force -Path $Dest | Out-Null
}

foreach ($Skill in $Skills) {
  $Target = Join-Path $Dest $Skill.Name

  if ($DryRun) {
    Write-Host "Would install $($Skill.Name) -> $Target"
    continue
  }

  if (Test-Path -LiteralPath $Target) {
    Remove-Item -LiteralPath $Target -Recurse -Force
  }

  Copy-Item -LiteralPath $Skill.FullName -Destination $Target -Recurse
  Write-Host "Installed $($Skill.Name) -> $Target"
}

Write-Host "Restart Codex to pick up new skills."

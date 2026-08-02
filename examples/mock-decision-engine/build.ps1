$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$runtime = Join-Path $root 'runtime'
New-Item -ItemType Directory -Path $runtime -Force | Out-Null

python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --name mock-engine `
  --distpath $runtime `
  --workpath (Join-Path $root '.build') `
  --specpath (Join-Path $root '.build') `
  (Join-Path $root 'mock_engine.py')

Write-Host "Built $runtime\mock-engine.exe"

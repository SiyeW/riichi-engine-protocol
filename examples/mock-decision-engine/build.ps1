$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $root '..\..'))
$python = Join-Path $projectRoot '.conda-build\python.exe'
$runtime = Join-Path $root 'runtime'

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
  throw 'Missing .conda-build environment. Create it from environment.yml at the repository root first.'
}

New-Item -ItemType Directory -Path $runtime -Force | Out-Null

& $python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --name mock-engine `
  --distpath $runtime `
  --workpath (Join-Path $root '.build') `
  --specpath (Join-Path $root '.build') `
  (Join-Path $root 'mock_engine.py')

if ($LASTEXITCODE -ne 0) {
  throw "PyInstaller failed with exit code $LASTEXITCODE."
}

Write-Host "Built $runtime\mock-engine.exe"

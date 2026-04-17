$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean Coacher.spec

Write-Host ""
Write-Host "Build concluido em: $ProjectRoot\\dist\\Coacher.exe"

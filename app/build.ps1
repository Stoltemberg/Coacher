$ErrorActionPreference = "Stop"

$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $AppRoot
$SiteRoot = Join-Path $RepoRoot "site"
$DesktopUiRoot = Join-Path $AppRoot "ui"
$SiteOutRoot = Join-Path $SiteRoot "out"
$DesktopExportRoot = Join-Path $SiteOutRoot "desktop"

Write-Host "==> Gerando frontend do coach desktop"
Set-Location $SiteRoot
npm ci
npm run build:desktop-ui

if (!(Test-Path (Join-Path $DesktopExportRoot "index.html"))) {
    throw "Export da UI desktop não encontrado em $DesktopExportRoot"
}

Write-Host "==> Sincronizando assets do desktop em app/ui"
if (Test-Path $DesktopUiRoot) {
    Get-ChildItem -Path $DesktopUiRoot -Force |
        Where-Object { $_.Name -ne ".gitignore" } |
        Remove-Item -Recurse -Force
} else {
    New-Item -ItemType Directory -Path $DesktopUiRoot | Out-Null
}

Copy-Item (Join-Path $SiteOutRoot "_next") $DesktopUiRoot -Recurse -Force
Copy-Item $DesktopExportRoot $DesktopUiRoot -Recurse -Force

if (Test-Path (Join-Path $SiteOutRoot "favicon.ico")) {
    Copy-Item (Join-Path $SiteOutRoot "favicon.ico") $DesktopUiRoot -Force
}

Get-ChildItem -Path $DesktopUiRoot -Recurse -Filter *.txt | Remove-Item -Force

if (!(Test-Path (Join-Path $DesktopUiRoot ".gitignore"))) {
    Set-Content -Path (Join-Path $DesktopUiRoot ".gitignore") -Value "*`n!.gitignore"
}

Write-Host "==> Empacotando app Python"
Set-Location $AppRoot
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --distpath dist --workpath build .\Coacher.spec

Write-Host ""
Write-Host "Build concluído em: $AppRoot\\dist\\Coacher.exe"

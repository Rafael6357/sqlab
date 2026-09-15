# SQLab — script de build reproducible (PyInstaller, onefile, windowed)
# Genera dist\SQLab.exe a partir de run.spec (raíz del repo).
# Requiere: python + PyInstaller (pip install pyinstaller).
# OJO: se invoca SIEMPRE con `python -m PyInstaller` para usar el mismo
# intérprete que ejecuta la app (evita binarios de otro Python del PATH).

[CmdletBinding()]
param()

$root = Split-Path -Parent $PSScriptRoot
$spec = Join-Path $root "run.spec"
$distDir = Join-Path $root "dist"

if (-not (Test-Path -LiteralPath $spec)) {
    Write-Error "No se encontró run.spec en la raíz del proyecto: $spec"
    exit 1
}

Write-Host "== SQLab build =="
Write-Host "  Spec : $spec"
Write-Host "  Python: $(python --version 2>&1)"

if (-not (python -m PyInstaller --version 2>$null)) {
    Write-Error "PyInstaller no está instalado en este intérprete. Instálalo con: python -m pip install pyinstaller"
    exit 1
}

Push-Location $root
try {
    # PyInstaller escribe el progreso por stderr; lo fusionamos sin
    # que PowerShell 5.1 lo interprete como error (2>&1).
    python -m PyInstaller --noconfirm --clean run.spec 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Error "PyInstaller falló con código $LASTEXITCODE"
        exit 1
    }
    $exe = Join-Path $distDir "SQLab.exe"
    if (Test-Path -LiteralPath $exe) {
        Write-Host "OK -> $exe"
    } else {
        Write-Error "El build terminó pero no se encontró dist\SQLab.exe"
        exit 1
    }
} finally {
    Pop-Location
}
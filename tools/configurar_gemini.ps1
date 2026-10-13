$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
$envPath = Join-Path $root '.env'
if (-not (Test-Path $python)) { throw 'No se encontro el entorno Python de EduTurnos.' }
if (-not (Test-Path $envPath)) { throw 'No se encontro la configuracion local .env.' }

$source = @'
import sys
from dotenv import set_key
key = sys.stdin.read().strip()
if not key:
    raise SystemExit('No se recibio una clave.')
set_key(sys.argv[1], 'GEMINI_API_KEY', key, quote_mode='always')
'@

$secureKey = Read-Host 'Introduce la clave de Gemini (entrada oculta)' -AsSecureString
$pointer = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try {
    $key = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    if ([string]::IsNullOrWhiteSpace($key)) { throw 'La clave no puede estar vacia.' }
    $key | & $python -c $source $envPath
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo guardar la configuracion de Gemini.' }
    Write-Host 'Clave guardada sin mostrarla. Reinicia EduTurnos para activar el chat.'
} finally {
    $key = $null
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    $secureKey.Dispose()
}
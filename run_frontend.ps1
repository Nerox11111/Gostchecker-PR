param(
  [int]$Port = 3000,
  [string]$StaticDir = "frontend\static"
)

$ErrorActionPreference = "Stop"

$resolved = Resolve-Path $StaticDir
python -m http.server $Port --directory $resolved


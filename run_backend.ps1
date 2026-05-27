param(
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
python -m uvicorn server:app --reload --port $Port


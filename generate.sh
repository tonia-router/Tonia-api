#!/usr/bin/env bash
# Regenerate TypeScript + Python clients from public.openapi.yaml (Docker).
# Usage:
#   ./generate.sh              # smoke output under ../.codegen-smoke/
#   ./generate.sh --sdk-repos  # write into ../{typescript,python}-sdk/generated/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_DIR="$(cd "$(dirname "$0")" && pwd)"
SPEC="$API_DIR/public.openapi.yaml"
IMAGE="${OPENAPI_GENERATOR_IMAGE:-openapitools/openapi-generator-cli:v7.14.0}"
MODE="smoke"

if [[ "${1:-}" == "--sdk-repos" ]]; then
  MODE="sdk"
elif [[ -n "${1:-}" ]]; then
  echo "usage: $0 [--sdk-repos]" >&2
  exit 2
fi

if [[ ! -f "$SPEC" ]]; then
  echo "missing spec: $SPEC" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required for OpenAPI Generator ($IMAGE)" >&2
  exit 1
fi

if [[ "$MODE" == "smoke" ]]; then
  TS_OUT="$ROOT/.codegen-smoke/typescript-fetch"
  PY_OUT="$ROOT/.codegen-smoke/python"
else
  # Keep hand-authored README / wrappers; only refresh generated/
  TS_OUT="$ROOT/typescript-sdk/generated"
  PY_OUT="$ROOT/python-sdk/generated"
fi

rm -rf "$TS_OUT" "$PY_OUT"
mkdir -p "$TS_OUT" "$PY_OUT"

echo "==> TypeScript (typescript-fetch) → $TS_OUT"
docker run --rm \
  -v "$API_DIR:/local:ro" \
  -v "$TS_OUT:/out" \
  "$IMAGE" generate \
  -i /local/public.openapi.yaml \
  -g typescript-fetch \
  -o /out \
  --additional-properties=npmName=@tonia/sdk,supportsES6=true,typescriptThreePlus=true,withoutRuntimeChecks=true,npmVersion=0.1.0

echo "==> Python → $PY_OUT"
docker run --rm \
  -v "$API_DIR:/local:ro" \
  -v "$PY_OUT:/out" \
  "$IMAGE" generate \
  -i /local/public.openapi.yaml \
  -g python \
  -o /out \
  --additional-properties=packageName=tonia_generated,projectName=tonia-generated,packageVersion=0.1.0,library=urllib3

# PEP 621 rejects bare license = "Proprietary" from the generator.
if [[ -f "$PY_OUT/pyproject.toml" ]]; then
  python3 - <<PY
from pathlib import Path
path = Path("$PY_OUT/pyproject.toml")
text = path.read_text(encoding="utf-8")
text = text.replace('license = "Proprietary"', 'license = { text = "Proprietary" }')
path.write_text(text, encoding="utf-8")
PY
fi

echo "==> Generated client integrity check"
python3 "$API_DIR/check_generated_clients.py" "$TS_OUT" "$PY_OUT"

echo "OK generated ($MODE)"

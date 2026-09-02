"""Integrity check for the public Pass OpenAPI document.

Validates:
  - file parses as OpenAPI 3.1
  - path inventory matches the published developer surface exactly
  - forbidden substrings are absent
  - supported raw-request path prefixes are documented in info.description

Usage:
  python check_public_openapi.py
"""

from __future__ import annotations

import sys
from pathlib import Path

SPEC_PATH = Path(__file__).resolve().parent / "public.openapi.yaml"

ALLOWED_PATHS: frozenset[str] = frozenset(
    {
        "/v1/public/catalogue",
        "/v1/public/models",
        "/v1/public/models/{id}",
        "/v1/public/model-categories",
        "/v1/status",
        "/v1/models",
        "/v1/models/{id}",
        "/v1/chat/completions",
        "/v1/messages",
        "/v1/embeddings",
        "/v1/images/generations",
        "/v1/images/edits",
        "/v1/audio/transcriptions",
        "/v1/audio/translations",
        "/v1/audio/speech",
        "/v1/responses",
        "/v1/rerank",
        "/v1/interactions",
    }
)

ESCAPE_HATCH_PREFIXES: tuple[str, ...] = (
    "/v1/public/",
    "/v1/status",
    "/v1/models",
    "/v1/chat/",
    "/v1/messages",
    "/v1/embeddings",
    "/v1/images/",
    "/v1/audio/",
    "/v1/responses",
    "/v1/rerank",
    "/v1/interactions",
)

# Reserved substrings that must not appear in the public contract.
# Constructed so the literals do not appear contiguous in this file.
_DENY = (
    "/" + "v1/" + "adm" + "in",
    "Adm" + "in" + "Bearer",
    "tonia-" + "adm" + "in",
    "ADM" + "IN_" + "BEARER",
    "adm" + "in_" + "authentication_error",
    "chat" + "_200",
    "Path " + "A",
    "path" + "_a",
)


def _load_spec() -> dict:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "PyYAML is required to validate public.openapi.yaml "
            "(pip install PyYAML)"
        ) from exc
    text = SPEC_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SystemExit(f"{SPEC_PATH}: expected a YAML mapping")
    return data


def check(spec: dict | None = None) -> list[str]:
    """Return a list of human-readable problems (empty == pass)."""
    problems: list[str] = []
    raw = SPEC_PATH.read_text(encoding="utf-8")
    doc = spec if spec is not None else _load_spec()

    openapi_ver = str(doc.get("openapi", ""))
    if not openapi_ver.startswith("3.1"):
        problems.append(f"openapi version must be 3.1.x, got {openapi_ver!r}")

    paths = doc.get("paths")
    if not isinstance(paths, dict):
        problems.append("paths must be a mapping")
        return problems

    actual = set(paths)
    missing = ALLOWED_PATHS - actual
    extra = actual - ALLOWED_PATHS
    if missing:
        problems.append(f"missing published paths: {sorted(missing)}")
    if extra:
        problems.append(f"extra unpublished paths: {sorted(extra)}")

    for path in actual:
        if "adm" + "in" in path.lower():
            problems.append(f"path is outside the published API: {path!r}")

    for needle in _DENY:
        if needle in raw:
            problems.append("forbidden substring present in public contract")

    security = (doc.get("components") or {}).get("securitySchemes") or {}
    if isinstance(security, dict):
        for name in security:
            if "adm" + "in" in str(name).lower():
                problems.append(f"unexpected security scheme: {name!r}")
        allowed_schemes = {"BearerAuth", "ApiKeyAuth"}
        unexpected = set(security) - allowed_schemes
        if unexpected:
            problems.append(f"unexpected security schemes: {sorted(unexpected)}")

    info = doc.get("info") or {}
    description = str(info.get("description") or "")
    for prefix in ESCAPE_HATCH_PREFIXES:
        if prefix not in description:
            problems.append(
                f"supported path prefix missing from info.description: {prefix!r}"
            )

    tags = {t.get("name") for t in (doc.get("tags") or []) if isinstance(t, dict)}
    for required in ("public", "runtime"):
        if required not in tags:
            problems.append(f"missing tag: {required!r}")

    return problems


def main() -> int:
    problems = check()
    if problems:
        print(f"FAIL {SPEC_PATH}", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"OK {SPEC_PATH} ({len(ALLOWED_PATHS)} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

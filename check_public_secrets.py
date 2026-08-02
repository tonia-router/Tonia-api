"""Refuse committed public artifacts that look like live credentials.

Scans sibling public trees (skills, sdk-examples, SDK READMEs). Placeholder
`TONIA_API_KEY` / `tonia_sk_...` style fakes are allowed when clearly fake.

Usage:
  python check_public_secrets.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCAN_ROOTS = (
    ROOT / "skills",
    ROOT / "sdk-examples",
    ROOT / "typescript-sdk" / "README.md",
    ROOT / "python-sdk" / "README.md",
    ROOT / "rust-sdk" / "README.md",
    ROOT / "tonia-api" / "README.md",
    ROOT / "tonia-api" / "API.md",
)

# Patterns that must never appear as live material in public trees.
_FORBIDDEN = (
    re.compile(r"ADMIN_[A-Z0-9_]*BEARER", re.I),
    re.compile(r"ACTOR_ASSERTION_KEY", re.I),
    re.compile(r"MEDIA_ANALYZER_AUTH_TOKEN", re.I),
    re.compile(r"sk-ant-api\d{2}-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    # Live-looking tonia keys: long random suffix (placeholders use obvious fakes).
    re.compile(r"tonia_(?:sk|live)_[A-Za-z0-9]{24,}"),
)

_SKIP_DIR_NAMES = {".git", "node_modules", "dist", "__pycache__", "generated", ".codegen-smoke"}


def _iter_files(root: Path):
    if root.is_file():
        yield root
        return
    if not root.is_dir():
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}:
            continue
        yield path


def check() -> list[str]:
    problems: list[str] = []
    for root in SCAN_ROOTS:
        for path in _iter_files(root):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pat in _FORBIDDEN:
                for match in pat.finditer(text):
                    value = match.group(0)
                    # Allow documented placeholders.
                    if "tonia_sk_..." in value or value.endswith("_test") or "example" in value.lower():
                        continue
                    if value in {"tonia_sk_test", "tonia_sk_placeholder"}:
                        continue
                    # openai-style sk- in docs about upstream — still refuse long keys
                    problems.append(f"{path}: possible secret {value[:24]}…")
                    break
    return problems


def main() -> int:
    problems = check()
    if problems:
        print("FAIL public secret scan", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"OK public secret scan ({len(SCAN_ROOTS)} roots)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

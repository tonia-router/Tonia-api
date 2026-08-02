"""Refuse generated SDK trees that include reserved internal substrings.

Usage:
  python check_generated_clients.py DIR [DIR ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

# Constructed so the literals do not appear contiguous in this file.
_FORBIDDEN = (
    "/" + "v1/" + "adm" + "in",
    "Adm" + "in" + "Bearer",
    "tonia-" + "adm" + "in",
    "ADM" + "IN_" + "BEARER",
    "adm" + "in_" + "authentication_error",
)

_SKIP_DIR_NAMES = {
    ".git",
    ".openapi-generator",
    ".pytest_cache",
    "node_modules",
    "dist",
    "__pycache__",
    ".venv",
    "venv",
}


def _iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIR_NAMES for part in path.parts):
            continue
        # Scan source + package metadata; skip binary-ish extensions.
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}:
            continue
        yield path


def check_tree(root: Path) -> list[str]:
    problems: list[str] = []
    if not root.is_dir():
        return [f"not a directory: {root}"]
    for path in _iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for needle in _FORBIDDEN:
            if needle in text:
                problems.append(f"{path}: reserved substring present")
                break
        reserved = "/" + "adm" + "in"
        lowered = text.lower()
        if "/v1" + reserved in lowered or '"' + reserved[1:] + "/" in lowered:
            problems.append(f"{path}: reserved path reference")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: check_generated_clients.py DIR [DIR ...]", file=sys.stderr)
        return 2
    all_problems: list[str] = []
    for arg in argv[1:]:
        all_problems.extend(check_tree(Path(arg).resolve()))
    if all_problems:
        print("FAIL generated client check", file=sys.stderr)
        for p in all_problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"OK generated client check ({len(argv) - 1} trees)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
"""Fail if any tracked source file contains an em dash (U+2014).

The product spec forbids em dashes anywhere in the repo. Run from the repo root.
"""

from __future__ import annotations

import sys
from pathlib import Path

EM_DASH = "\u2014"
SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    ".venv",
    "venv",
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    "var",
}
SKIP_FILES = {"package-lock.json", "check_no_emdash.py"}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    offenders: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in SKIP_FILES or set(path.parts) & SKIP_DIRS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if EM_DASH in line:
                offenders.append(f"{path.relative_to(root)}:{lineno}: {line.strip()}")

    if offenders:
        print("Em dash (U+2014) found:")
        for item in offenders:
            print(f"  {item}")
        return 1
    print("No em dashes found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

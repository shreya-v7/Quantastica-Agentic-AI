"""Explicit seed loader CLI: `python -m app.seed [load|reset]`."""

from __future__ import annotations

import sys

from app.core.config import get_settings
from app.infra.factory import build_container
from app.seed import loader


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "load"
    repository = build_container(get_settings()).repository
    if action == "reset":
        counts = loader.reset(repository)
    elif action == "load":
        counts = loader.load_into(repository)
    else:
        raise SystemExit(f"Unknown action '{action}'. Use 'load' or 'reset'.")
    print(f"seed {action}: {counts}")


if __name__ == "__main__":
    main()

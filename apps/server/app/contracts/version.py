"""Single contract version — must match `packages/types/contracts.json`."""

from __future__ import annotations

import json
from pathlib import Path


def read_contract_version() -> str:
    """Resolve repo-root `packages/types/contracts.json`."""
    here = Path(__file__).resolve()
    # apps/server/app/contracts/version.py → parents[4] = monorepo root
    repo_root = here.parents[4]
    path = repo_root / "packages" / "types" / "contracts.json"
    if not path.is_file():
        return "1.0.0"
    data = json.loads(path.read_text(encoding="utf-8"))
    return str(data.get("version", "1.0.0"))


CONTRACT_VERSION = read_contract_version()

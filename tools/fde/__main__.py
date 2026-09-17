"""Onboard a CA or wealth-firm tenant from a JSON config plus a layout pack."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.fde import health, layout_for, load_spec


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["onboard", "health"])
    parser.add_argument("--config", default="tenants/northstar.json")
    args = parser.parse_args()
    if args.command == "onboard":
        spec = load_spec(args.config)
        layouts = {employer: layout_for(employer) for employer in spec.employers}
        print(json.dumps({
            "tenantId": spec.tenant_id,
            "name": spec.name,
            "segment": spec.segment,
            "layouts": layouts,
        }, indent=2))
        return
    print(json.dumps(health(0.2, 0, 0, 999, 0.1, 0.5), indent=2))


if __name__ == "__main__":
    main()

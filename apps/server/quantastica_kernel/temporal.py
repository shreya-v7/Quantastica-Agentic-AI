"""Pure bitemporal reconstruction. Unknown history returns None, never a guessed book."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime

from .exceptions.snapshot import BookSnapshot


def instant(value: datetime | str) -> datetime:
    stamp = datetime.fromisoformat(value) if isinstance(value, str) else value
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("Temporal queries require a timezone")
    return stamp


def reconstruct(events: list[dict], valid_time: datetime, recorded_time: datetime):
    valid, recorded = instant(valid_time), instant(recorded_time)
    eligible = sorted(
        (e for e in events if instant(e["valid_time"]) <= valid
         and instant(e["recorded_time"]) <= recorded),
        key=lambda e: (instant(e["valid_time"]), instant(e["recorded_time"]), e["seq"]),
    )
    state = None
    for event in eligible:
        data = deepcopy(event["payload"])
        if event["event_type"] == "book.snapshot":
            state = data
        elif event["event_type"] == "book.patch":
            if state is None:
                raise ValueError("Patch precedes initial household snapshot")
            for key in ("household_name", "tax", "as_of"):
                if key in data:
                    state[key] = data[key]
            lots = {lot["id"]: lot for lot in state["lots"]}
            for lot_id in data.get("lots_remove", []):
                lots.pop(lot_id, None)
            for lot in data.get("lots_upsert", []):
                lots[lot["id"]] = lot
            for change in data.get("lot_quantities", []):
                if change["id"] not in lots:
                    raise ValueError("Quantity event references a missing lot")
                lots[change["id"]]["quantity"] = change["quantity"]
            state["lots"] = list(lots.values())
        else:
            raise ValueError(f"Unknown book event: {event['event_type']}")
    if state is None:
        return None
    state["lots"].sort(key=lambda lot: lot["id"])
    return BookSnapshot.model_validate(state)


def snapshot_patch(before: BookSnapshot, after: BookSnapshot) -> dict:
    old, new = before.model_dump(mode="json"), after.model_dump(mode="json")
    patch = {k: new[k] for k in ("household_name", "tax", "as_of") if old[k] != new[k]}
    old_lots = {lot["id"]: lot for lot in old["lots"]}
    new_lots = {lot["id"]: lot for lot in new["lots"]}
    patch["lots_remove"] = sorted(set(old_lots) - set(new_lots))
    patch["lots_upsert"] = [new_lots[k] for k in sorted(new_lots)
                            if old_lots.get(k) != new_lots[k]]
    return patch

from __future__ import annotations
import json, pathlib, time

STATE_FILE = pathlib.Path(".state/seen.json")

def load_seen() -> set[str]:
    """
    Load posted IDs from .state/seen.json.
    Returns an empty set if the file doesn't exist or is malformed.
    """
    try:
        raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        # supports both legacy (list) and structured {"ids":[...]} formats
        if isinstance(raw, list):
            return set(raw)
        if isinstance(raw, dict) and "ids" in raw and isinstance(raw["ids"], list):
            return set(raw["ids"])
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return set()

def save_seen(ids: set[str], keep_last: int = 5000) -> None:
    """
    Persist up to keep_last IDs. Stores a little metadata for sanity.
    """
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Keep at most keep_last elements (order doesn't matter for de-dupe)
    out = list(ids)
    if len(out) > keep_last:
        out = out[-keep_last:]
    payload = {"ids": out, "updated_unix": int(time.time())}
    STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

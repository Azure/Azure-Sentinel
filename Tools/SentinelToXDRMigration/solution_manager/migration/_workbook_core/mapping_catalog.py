"""Read the versioned package-local mapping snapshot without live resolution."""
from functools import lru_cache
from importlib.resources import files
import json


@lru_cache(maxsize=1)
def load_mapping_catalog() -> dict:
    return json.loads(files(__package__).joinpath("data/mapping_catalog.json").read_text("utf-8"))


def tier_of(table: str, *, allowed_tables=()) -> str:
    allowed = set(allowed_tables or ())
    entry = load_mapping_catalog()["tables"].get(table)
    if entry:
        if entry["tier"] == "blocked" and table in allowed:
            return "1to1"
        return entry["tier"]
    if isinstance(table, str) and (table.endswith("_CL") or table in allowed):
        return "1to1"
    return "unknown"

#!/usr/bin/env python3
"""
Generates the 26.3 overlay for a pack from its 26.2 base tree.

26.3 renamed a number of fields. Rather than keep two hand-edited copies of
every file, the base tree stays in 26.2 form (that is what the loot editor
reads and writes) and this regenerates  v26_3/data/  from it on every build.
Only files that actually differ end up in the overlay; everything else falls
through to the base tree.

Changes applied, per the 26.3 changelog and confirmed against a 26.3 server:
  * block states:      "Name" -> "id", "Properties" -> "properties"
  * structure spawns:  "minCount"/"maxCount" -> "count" (an int provider)
  * loot pool entries: "functions" -> "modifier"
  * predicates:        the "condition" field naming the type -> "type"
  * item modifiers:    the "function" field naming the type -> "type"
  * number providers:  an inline one must name its type; it used to default
"""
import json
from pathlib import Path

OVERLAY = "v26_3"


def int_provider(low, high):
    if low == high:
        return low
    return {"type": "minecraft:uniform", "min_inclusive": low, "max_inclusive": high}


def convert_predicate(obj):
    """A predicate names its type in "type" now, not "condition"."""
    if isinstance(obj, dict) and isinstance(obj.get("condition"), str):
        renamed = {"type": obj["condition"]}
        renamed.update({k: v for k, v in obj.items() if k != "condition"})
        return convert(renamed)
    return convert(obj)


def convert_modifier(obj):
    """An item modifier names its type in "type" now, not "function"."""
    if isinstance(obj, dict) and isinstance(obj.get("function"), str):
        renamed = {"type": obj["function"]}
        renamed.update({k: v for k, v in obj.items() if k != "function"})
        return convert(renamed)
    return convert(obj)


def convert(obj):
    if isinstance(obj, list):
        return [convert(v) for v in obj]
    if not isinstance(obj, dict):
        return obj

    out = {}
    for key, value in obj.items():
        if key == "Name":
            out["id"] = convert(value)
        elif key == "Properties":
            out["properties"] = convert(value)
        elif key == "functions":
            out["modifier"] = [convert_modifier(v) for v in value]
        elif key == "conditions":
            out["conditions"] = [convert_predicate(v) for v in value]
        else:
            out[key] = convert(value)
    return out


def convert_spawns(obj):
    """minCount/maxCount collapse into a single int-provider count field."""
    if isinstance(obj, list):
        return [convert_spawns(v) for v in obj]
    if not isinstance(obj, dict):
        return obj
    if "minCount" in obj and "maxCount" in obj:
        rest = {k: convert_spawns(v) for k, v in obj.items()
                if k not in ("minCount", "maxCount")}
        rest["count"] = int_provider(obj["minCount"], obj["maxCount"])
        return rest
    return {k: convert_spawns(v) for k, v in obj.items()}


def name_number_providers(obj):
    """An inline number provider must name its type now; it used to default."""
    if isinstance(obj, list):
        return [name_number_providers(v) for v in obj]
    if not isinstance(obj, dict):
        return obj
    if set(obj) == {"min", "max"}:
        return {"type": "minecraft:uniform", **obj}
    return {k: name_number_providers(v) for k, v in obj.items()}


def generate(pack_dir):
    """Rewrite the pack's overlay. Returns the number of files written."""
    pack_dir = Path(pack_dir)
    base, overlay = pack_dir / "data", pack_dir / OVERLAY / "data"
    if not base.is_dir():
        return 0   # a resource pack has nothing 26.3 changes

    for stale in overlay.rglob("*.json"):
        stale.unlink()

    written = 0
    for path in sorted(base.rglob("*.json")):
        original = json.loads(path.read_text(encoding="utf-8"))
        converted = convert(convert_spawns(original))
        if "/loot_table/" in path.as_posix():
            converted = name_number_providers(converted)
        if converted == original:
            continue
        target = overlay / path.relative_to(base)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(converted, indent=2), encoding="utf-8")
        written += 1

    for empty in sorted(overlay.rglob("*"), reverse=True):
        if empty.is_dir() and not any(empty.iterdir()):
            empty.rmdir()
    overlay.mkdir(parents=True, exist_ok=True)
    (overlay / ".gitkeep").touch()
    return written


if __name__ == "__main__":
    import sys
    src = Path(__file__).resolve().parent.parent / "src"
    for slug in (sys.argv[1:] or sorted(p.name for p in src.iterdir() if (p / "pack.json").is_file())):
        print(f"{slug}: {generate(src / slug)} overlay files")

#!/usr/bin/env python3
"""
Loot builder for Luki's refresh packs.

Double-clicked (no arguments) it does the whole job:
  * reads every  loot/<pack>.yml
  * patches the matching pack's  .zip  AND  .jar  (kept in sync)
  * checks item names against the vanilla item list and refuses to build
    if one is misspelled, telling the owner exactly which line is wrong

Maintainer commands:
  build_loot.py extract  <pack.zip> <out.yml>   # regenerate a loot.yml from a pack
  build_loot.py build    <pack.zip> <loot.yml>  # patch a single archive
"""
import sys, os, json, zipfile, io
from collections import OrderedDict

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required (pip install pyyaml).")


# ---------------------------------------------------------------- paths / data
def base_dir():
    """Folder the exe/script lives in (the collection root when shipped)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource(name):
    """A bundled data file, whether frozen by PyInstaller or run as source."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, name)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)


def load_vanilla_items():
    try:
        return set(json.load(open(resource("items.json"), encoding="utf-8")))
    except Exception:
        return set()  # validation simply skipped if the list is missing


VANILLA = load_vanilla_items()


def _norm_item(name):
    return name.split(":", 1)[1] if ":" in name else name


def _is_known(name):
    # Only judge vanilla (minecraft:) or unprefixed names; leave other
    # namespaces (another datapack's custom items) alone.
    ns = name.split(":", 1)[0] if ":" in name else "minecraft"
    if ns != "minecraft" or not VANILLA:
        return True
    return _norm_item(name) in VANILLA


# ---------------------------------------------------------------- yaml helpers
def _represent_odict(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())
yaml.add_representer(OrderedDict, _represent_odict)


def _num(s):
    s = str(s).strip()
    return float(s) if "." in s else int(s)


# ---------------------------------------------------------------- table <-> yaml
def _find_setcount(entry):
    for f in entry.get("functions", []) or []:
        if f.get("function") == "minecraft:set_count":
            return f
    return None


def _amount_from_setcount(func):
    if not func:
        return None
    c = func.get("count")
    if isinstance(c, dict) and c.get("type") == "minecraft:uniform":
        return f'{c["min"]}-{c["max"]}'
    if isinstance(c, (int, float)):
        return int(c)
    return None


def _rolls_friendly(rolls):
    if isinstance(rolls, dict) and rolls.get("type") == "minecraft:uniform":
        return f'{rolls["min"]}-{rolls["max"]}'
    if isinstance(rolls, (int, float)):
        return int(rolls)
    return None


def _key_of(name):
    """zip entry name -> friendly table key (ns/short)."""
    ns = name.split("/", 2)[1]
    short = name.split("/loot_table/", 1)[1][:-5]
    return f"{ns}/{short}"


def _loot_names(z):
    return [n for n in z.namelist() if "/loot_table/" in n and n.endswith(".json")]


def _pool_to_block(pool):
    """One pool -> an OrderedDict with draws + loot rows (item entries only)."""
    rows = []
    for e in pool.get("entries", []):
        if e.get("type") != "minecraft:item":
            continue
        row = OrderedDict(item=e.get("name", "?"), rarity=e.get("weight", 1))
        amt = _amount_from_setcount(_find_setcount(e))
        if amt is not None:
            row["amount"] = amt
        rows.append(row)
    block = OrderedDict()
    draws = _rolls_friendly(pool.get("rolls"))
    if draws is not None:
        block["draws"] = draws
    block["loot"] = rows
    return block


def extract(zip_path, yml_path):
    tables = OrderedDict()
    with zipfile.ZipFile(zip_path) as z:
        for n in sorted(_loot_names(z)):
            data = json.loads(z.read(n))
            pools = data.get("pools") or [{}]
            if len(pools) == 1:
                tables[_key_of(n)] = _pool_to_block(pools[0])
            else:
                # Multiple pools: keep them as a list so every item is editable.
                tables[_key_of(n)] = OrderedDict(
                    pools=[_pool_to_block(p) for p in pools])
    with open(yml_path, "w", encoding="utf-8") as f:
        f.write(HEADER)
        yaml.dump(OrderedDict(tables=tables), f, default_flow_style=False,
                  sort_keys=False, allow_unicode=True)
    print(f"  wrote {os.path.basename(yml_path)}  ({len(tables)} tables)")


def _apply_amount(entry, amount):
    if isinstance(amount, str) and "-" in amount:
        lo, hi = amount.split("-", 1)
        count = {"type": "minecraft:uniform", "min": _num(lo), "max": _num(hi)}
    else:
        count = int(amount)
    sc = _find_setcount(entry)
    if sc is None:
        entry.setdefault("functions", []).append(
            {"function": "minecraft:set_count", "count": count})
    else:
        sc["count"] = count


def _spec_pools(spec):
    """Yield the loot-row lists in a table spec (single- or multi-pool)."""
    if "pools" in spec:
        for blk in spec["pools"]:
            yield blk
    else:
        yield spec


def validate(cfg, yml_name):
    """Return a list of friendly error strings (empty = all good)."""
    errors = []
    for tkey, spec in (cfg.get("tables") or {}).items():
        for blk in _spec_pools(spec):
            for i, row in enumerate(blk.get("loot", []) or [], 1):
                item = row.get("item")
                if not item:
                    errors.append(f'{yml_name}: an entry in "{tkey}" is missing its item name.')
                    continue
                if not _is_known(item):
                    errors.append(
                        f'{yml_name}: "{item}" (item #{i} in "{tkey}") is not a real '
                        f'Minecraft item. Check the spelling.')
    return errors


def _patch_pool(pool, blk):
    """Apply one YAML block (draws + loot rows) onto one JSON pool, in place."""
    if "draws" in blk:
        d = blk["draws"]
        pool["rolls"] = ({"type": "minecraft:uniform",
                          "min": _num(str(d).split("-")[0]),
                          "max": _num(str(d).split("-")[1])}
                         if isinstance(d, str) and "-" in d else int(d))
    item_idx = [i for i, e in enumerate(pool["entries"])
                if e.get("type") == "minecraft:item"]
    non_item = [e for e in pool["entries"] if e.get("type") != "minecraft:item"]
    new = []
    for i, row in enumerate(blk.get("loot", [])):
        e = pool["entries"][item_idx[i]] if i < len(item_idx) else {"type": "minecraft:item"}
        e["name"] = row["item"]
        r = int(row.get("rarity", 1))
        # Only write an explicit weight when it matters; a lone weight:1 is the
        # default, so leave it off to keep unchanged tables byte-for-byte clean.
        if r != 1 or "weight" in e:
            e["weight"] = r
        if "amount" in row:
            _apply_amount(e, row["amount"])
        new.append(e)
    pool["entries"] = new + non_item


def build(zip_path, yml_path):
    with open(yml_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    tables = cfg.get("tables", {})

    src = zipfile.ZipFile(zip_path)
    buf = io.BytesIO()
    out = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    patched = 0
    name_of = {n: _key_of(n) for n in _loot_names(src)}

    for n in src.namelist():
        raw = src.read(n)
        key = name_of.get(n)
        if key in tables:
            data = json.loads(raw)
            spec = tables[key]
            blocks = spec["pools"] if "pools" in spec else [spec]
            for pi, blk in enumerate(blocks):
                if pi >= len(data["pools"]):
                    break
                _patch_pool(data["pools"][pi], blk)
            raw = json.dumps(data, indent=2).encode("utf-8")
            patched += 1
        out.writestr(n, raw)

    src.close(); out.close()
    with open(zip_path, "wb") as f:
        f.write(buf.getvalue())
    return patched


# ---------------------------------------------------------------- double-click
def _pack_folder_for(yml_stem, root):
    """loot/grand-capitals.yml -> the 'grand capitals' folder."""
    target = yml_stem.replace("-", " ").lower()
    for d in os.listdir(root):
        if os.path.isdir(os.path.join(root, d)) and d.lower() == target:
            return os.path.join(root, d)
    return None


def run_all():
    root = base_dir()
    loot_dir = os.path.join(root, "loot")
    if not os.path.isdir(loot_dir):
        print("Could not find the 'loot' folder next to this program.")
        return 1
    ymls = sorted(f for f in os.listdir(loot_dir) if f.endswith((".yml", ".yaml")))
    if not ymls:
        print("No loot settings files found in the 'loot' folder.")
        return 1

    # Validate everything FIRST so nothing is half-written on an error.
    all_errors, jobs = [], []
    for y in ymls:
        ypath = os.path.join(loot_dir, y)
        cfg = yaml.safe_load(open(ypath, encoding="utf-8")) or {}
        all_errors += validate(cfg, y)
        folder = _pack_folder_for(os.path.splitext(y)[0], root)
        if not folder:
            all_errors.append(f'{y}: could not find a matching pack folder.')
            continue
        archives = [os.path.join(folder, f) for f in os.listdir(folder)
                    if f.endswith((".zip", ".jar"))]
        jobs.append((y, ypath, archives))

    if all_errors:
        print("Nothing was changed. Please fix these first:\n")
        for e in all_errors:
            print("  - " + e)
        return 1

    total = 0
    for y, ypath, archives in jobs:
        print(f"{y}:")
        for arc in archives:
            n = build(arc, ypath)
            total += 1
            print(f"    updated {os.path.basename(arc)}  ({n} tables)")
    print(f"\nDone. Updated {total} pack files. "
          f"Re-import the pack(s) into your world to see the new loot.")
    return 0


HEADER = """# =============================================================
#  LOOT SETTINGS
#  Change the numbers, save this file, then run Build-Loot.
#
#  rarity  = how often an item shows up. Higher = more common.
#            (it's a share of the total, not a percentage)
#  amount  = how many you get. "1-3" means 1 to 3; a single
#            number means always exactly that many.
#  draws   = how many times the container rolls for an item.
#
#  Delete a line to remove that item. Copy a line to add one.
#  Spell item names exactly, e.g. minecraft:diamond
# =============================================================
"""


def main():
    if len(sys.argv) == 1:
        code = run_all()
        if sys.stdout.isatty() or getattr(sys, "frozen", False):
            try:
                input("\nPress Enter to close...")
            except EOFError:
                pass
        sys.exit(code)
    mode = sys.argv[1]
    if mode == "extract":
        extract(sys.argv[2], sys.argv[3])
    elif mode == "build":
        print(f"patched {build(sys.argv[2], sys.argv[3])} tables in "
              f"{os.path.basename(sys.argv[2])}")
    else:
        sys.exit(f"unknown command: {mode}")


if __name__ == "__main__":
    main()

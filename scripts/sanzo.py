#!/usr/bin/env python3
"""Pick color combinations from Wada Sanzo's Dictionary of Color Combinations.

Data: data/colors.json (159 colors, 348 combinations: 1-120 have two colors,
121-240 three, 241-348 four). Stdlib only.

  sanzo.py random [--size 2|3|4] [--seed N]
  sanzo.py color <name | index | #hex>
  sanzo.py combo <number>

Every run writes a swatch page and prints its path. Use --out PATH to choose
the file, --no-html to skip it, and --json for machine-readable output.
"""

import argparse
import difflib
import html
import json
import random
import re
import sys
import tempfile
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "colors.json"


def load():
    colors = json.loads(DATA.read_text())["colors"]
    combos = {}
    for c in colors:
        for n in c["combinations"]:
            combos.setdefault(n, []).append(c)
    return colors, dict(sorted(combos.items()))


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return [int(h[i : i + 2], 16) for i in (0, 2, 4)]


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", re.sub(r"['’]", "", s.lower())).strip()


def find_color(colors, query):
    """Return (color, note). note explains a non-exact match, else None."""
    q = query.strip()
    if re.fullmatch(r"#?[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}", q):
        target = hex_to_rgb(q)
        best = min(colors, key=lambda c: sum((a - b) ** 2 for a, b in zip(c["rgb"], target)))
        dist = sum((a - b) ** 2 for a, b in zip(best["rgb"], target)) ** 0.5
        note = None if dist == 0 else f"nearest color to {q} (RGB distance {dist:.0f})"
        return best, note
    if q.isdigit():
        i = int(q)
        for c in colors:
            if c["index"] == i:
                return c, None
        sys.exit(f"No color with index {i} (valid: 1-{len(colors)}).")
    key = norm(q)
    names = {}
    for c in colors:
        for n in [c["name"], *c.get("aliases", [])]:
            names.setdefault(norm(n), c)
    if key in names:
        c = names[key]
        return c, None if norm(c["name"]) == key else f"'{q}' is listed as {c['name']}"
    subs = list({c["index"]: c for n, c in names.items() if key in n}.values())
    if len(subs) == 1:
        return subs[0], f"matched '{q}' to {subs[0]['name']}"
    if len(subs) > 1:
        sys.exit(f"'{q}' matches several colors: " + ", ".join(c["name"] for c in subs))
    close = difflib.get_close_matches(key, names, n=3, cutoff=0.5)
    if close:
        c = names[close[0]]
        others = [names[n]["name"] for n in close[1:] if names[n] is not c]
        also = f" (also close: {', '.join(others)})" if others else ""
        return c, f"no exact match for '{q}'; using {c['name']}{also}"
    sys.exit(f"No color matches '{q}'. Try a name, an index 1-{len(colors)}, or a hex value.")


def combo_record(n, members):
    return {
        "combination": n,
        "colors": [{"name": c["name"], "hex": c["hex"], "index": c["index"]} for c in members],
    }


def print_text(title, records, note=None):
    print(title)
    if note:
        print(f"({note})")
    for r in records:
        print(f"\nCombination {r['combination']}")
        for c in r["colors"]:
            print(f"  {c['hex']}  {c['name']}")


def write_html(path, title, records):
    blocks = []
    for r in records:
        bands = "".join(
            f'<div class="band" style="background:{c["hex"]}">'
            f'<span>{html.escape(c["name"])}<br>{c["hex"]}</span></div>'
            for c in r["colors"]
        )
        blocks.append(
            f'<figure><div class="swatch">{bands}</div>'
            f'<figcaption>No. {r["combination"]}</figcaption></figure>'
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wada Sanzo Combinations</title><style>
:root{{--bg:#f6f3ec;--fg:#222}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1c1b19;--fg:#eee}}}}
body{{background:var(--bg);color:var(--fg);font:14px/1.4 ui-sans-serif,system-ui,sans-serif;margin:0;padding:24px 16px}}
h1{{font-size:18px;font-weight:600;margin:0 0 20px}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:20px}}
figure{{margin:0}}
.swatch{{display:flex;flex-direction:column;height:260px;border-radius:4px;overflow:hidden}}
.band{{flex:1;display:flex;align-items:flex-end;padding:8px}}
.band span{{font-size:11px;background:rgba(255,255,255,.85);color:#222;padding:2px 5px;border-radius:2px}}
figcaption{{margin-top:6px}}
</style></head><body><h1>{html.escape(title)}</h1><main>{''.join(blocks)}</main></body></html>
"""
    )


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--json", action="store_true", help="print JSON")
    p.add_argument("--out", metavar="PATH", help="swatch page path (default: a wada-sanzo folder in the temp dir)")
    p.add_argument("--no-html", action="store_true", help="do not write a swatch page")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("random", help="draw one random combination")
    r.add_argument("--size", type=int, choices=[2, 3, 4], help="only combinations with this many colors")
    r.add_argument("--seed", type=int)
    c = sub.add_parser("color", help="all combinations that use a color")
    c.add_argument("query", nargs="+", help="color name, index, or #hex")
    k = sub.add_parser("combo", help="show one combination by number")
    k.add_argument("number", type=int)
    a = p.parse_args()

    colors, combos = load()
    note = None
    if a.cmd == "random":
        pool = [n for n, m in combos.items() if a.size is None or len(m) == a.size]
        n = random.Random(a.seed).choice(pool)
        records = [combo_record(n, combos[n])]
        title = f"Random combination (from {len(pool)})"
        stem = f"combo-{n}"
        payload = records[0]
    elif a.cmd == "combo":
        if a.number not in combos:
            sys.exit(f"No combination {a.number} (valid: 1-{max(combos)}).")
        records = [combo_record(a.number, combos[a.number])]
        title = f"Combination {a.number} ({len(combos[a.number])} colors)"
        stem = f"combo-{a.number}"
        payload = records[0]
    else:
        color, note = find_color(colors, " ".join(a.query))
        records = [combo_record(n, combos[n]) for n in sorted(color["combinations"])]
        title = f"{color['name']} {color['hex']} (color {color['index']}): {len(records)} combination{'' if len(records) == 1 else 's'}"
        stem = "color-" + norm(color["name"]).replace(" ", "-")
        payload = {
            "color": {k: color[k] for k in ("index", "name", "hex", "cmyk", "rgb")},
            "note": note,
            "combinations": records,
        }

    page = None
    if not a.no_html:
        page = Path(a.out) if a.out else Path(tempfile.gettempdir()) / "wada-sanzo" / f"{stem}.html"
        write_html(page, title, records)

    if a.json:
        if page:
            payload = {**payload, "swatch_page": str(page)}
        print(json.dumps(payload, indent=2))
    else:
        print_text(title, records, note)
        if page:
            print(f"\nSwatch page: {page}")


if __name__ == "__main__":
    main()

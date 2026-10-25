---
name: wada-sanzo
description: "Japanese color combinations from Wada Sanzo's Dictionary of Color Combinations (159 colors, 348 combinations). Use when someone wants a palette, a random color combo, colors that go with a given color, or mentions Wada Sanzo, Sanzo Wada, or the Dictionary of Color Combinations."
---

# Wada Sanzo color combinations

`data/colors.json` holds 159 colors and 348 combinations. Combinations 1-120
have two colors, 121-240 three, 241-348 four. Hex values are screen
approximations of the printed colors, so treat them as close, not exact.

`<skill>` below is this skill's directory (canonical copy:
`~/.agents/skills/wada-sanzo`). The script is stdlib Python.

## Pick the mode

- **No color given** ("give me a palette", "random Wada combo"): draw one.
  ```bash
  python3 <skill>/scripts/sanzo.py random            # any size
  python3 <skill>/scripts/sanzo.py random --size 3   # only 3-color combos
  ```
- **A color given** ("what goes with Cobalt Green", "combos for #c0392b"):
  list every combination that uses it.
  ```bash
  python3 <skill>/scripts/sanzo.py color "cobalt green"
  python3 <skill>/scripts/sanzo.py color 42        # by color index
  python3 <skill>/scripts/sanzo.py color "#c0392b" # nearest dictionary color
  ```
  Names match exactly (old spellings such as "Cerulian Blue" also work), then
  by part of a name, then by close spelling. A hex value maps to the nearest
  dictionary color by RGB distance. When the match is not exact the script
  prints a note; tell the user which color it used.
- **A combination number** ("show me combo 214"):
  `python3 <skill>/scripts/sanzo.py combo 214`

Flags go before the subcommand: `--json` for structured output, `--out PATH`
to choose where the swatch page goes, `--no-html` to skip it.

## Show the result

Every run writes an HTML swatch page and prints `Swatch page: <path>`. Give
the user the color names and hex values in text, then show that page: send it
with the file-sending tool if you have one, or open it. For a color with many
combinations (some have 15+), list all of them in text but keep prose short.

Do not link to outside color sites. Do not invent combinations or hex values;
only report what the script returns.

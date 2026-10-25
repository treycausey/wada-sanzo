# wada-sanzo

An agent skill (Claude Code and other `SKILL.md`-based agents) that picks color
combinations from Wada Sanzo's *A Dictionary of Color Combinations*: 159
colors and 348 combinations.

- Draw a random combination, optionally with 2, 3 or 4 colors.
- Give one color (name, index, or hex) and get every combination that uses it.
  A hex value maps to the nearest dictionary color.
- Every run writes an HTML swatch page.

## Install

```bash
git clone https://github.com/treycausey/wada-sanzo ~/.claude/skills/wada-sanzo
```

Then ask your agent for "a Wada Sanzo palette" or "what goes with Cerulean Blue".

## Use the script directly

Python 3, standard library only.

```bash
python3 scripts/sanzo.py random --size 3
python3 scripts/sanzo.py color "cerulean blue"
python3 scripts/sanzo.py color "#c0392b"
python3 scripts/sanzo.py combo 214
python3 scripts/sanzo.py --json --out palette.html random
```

## Data

`data/colors.json` comes from
[mattdesl/dictionary-of-colour-combinations](https://github.com/mattdesl/dictionary-of-colour-combinations)
(MIT). Hex values there are converted from the book's CMYK values with an ICC
profile, so they are screen approximations of the printed colors.

Changes from that file:

- Names respelled to match Ridgway's *Color Standards and Color Nomenclature*
  (1912), the source of Wada's English names. For example: Cerulian Blue →
  Cerulean Blue, Antwarp Blue → Antwerp Blue, Vistoris Lake → Victoria Lake,
  Krongbergs Green → Kronberg's Green. The original spellings are kept as
  `aliases` and still work as lookups.
- "Eugenia Red | A/B" and "Grayish Lavender - A/B" are renamed "Eugenia Red
  A/B" and "Grayish Lavender A/B".

`tests/` checks that combinations 1-120 have two colors, 121-240 three, and
241-348 four, matching the book's sections.

```bash
python3 -m unittest discover -s tests
```

## License

MIT. See [LICENSE](LICENSE).

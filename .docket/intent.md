# wada-sanzo

wada-sanzo is an agent skill for Claude Code and other agents that use SKILL.md. It picks color combinations from Wada Sanzo's "A Dictionary of Color Combinations", which has 159 colors and 348 combinations. The standard-library Python script `scripts/sanzo.py` can draw a random combination of 2, 3 or 4 colors, list every combination that uses a given color (by name, index or nearest hex match), or show one combination by number. Every run writes an HTML swatch page, and `--json` gives JSON output. The data in `data/colors.json` comes from mattdesl/dictionary-of-colour-combinations (MIT). It has been changed on purpose: names are respelled to match Ridgway, and the original spellings are kept as aliases. Tests in `tests/` check the combination sizes for each section of the book.

## Paths agents must not touch

- `data/LICENSE-mattdesl.md`: License for the third-party color data from Matt DesLauriers, which must stay unchanged
- `LICENSE`: The project's MIT license text
- `**/__pycache__`: Generated Python bytecode
- `**/*.pyc`: Generated Python bytecode

nogo: data/LICENSE-mattdesl.md
nogo: LICENSE
nogo: **/__pycache__
nogo: **/*.pyc

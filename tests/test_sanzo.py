"""Run with: python3 -m unittest discover -s tests"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "sanzo.py"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)


def run_json(*args):
    r = run("--json", "--no-html", *args)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


class DataTest(unittest.TestCase):
    def test_combination_sizes_match_book_sections(self):
        colors = json.loads((ROOT / "data" / "colors.json").read_text())["colors"]
        self.assertEqual(len(colors), 159)
        combos = {}
        for c in colors:
            for n in c["combinations"]:
                combos.setdefault(n, []).append(c["name"])
        self.assertEqual(sorted(combos), list(range(1, 349)))
        for n, members in combos.items():
            expected = 2 if n <= 120 else 3 if n <= 240 else 4
            self.assertEqual(len(members), expected, f"combination {n}: {members}")


class CliTest(unittest.TestCase):
    def test_random_is_repeatable_with_seed(self):
        self.assertEqual(run_json("random", "--seed", "3"), run_json("random", "--seed", "3"))

    def test_random_size_filter(self):
        for size in (2, 3, 4):
            self.assertEqual(len(run_json("random", "--size", str(size))["colors"]), size)

    def test_color_by_old_spelling(self):
        out = run_json("color", "Cerulian Blue")
        self.assertEqual(out["color"]["name"], "Cerulean Blue")
        self.assertIn(1, [r["combination"] for r in out["combinations"]])

    def test_color_ignores_apostrophes(self):
        self.assertEqual(run_json("color", "kronbergs green")["color"]["name"], "Kronberg's Green")

    def test_color_by_hex_uses_nearest(self):
        out = run_json("color", "#0093a5")
        self.assertEqual(out["color"]["name"], "Cerulean Blue")
        self.assertIsNone(out["note"])

    def test_ambiguous_name_fails_with_choices(self):
        r = run("color", "eugenia red")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Eugenia Red A", r.stderr)

    def test_combo_out_of_range(self):
        r = run("combo", "349")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("1-348", r.stderr)

    def test_swatch_page_written_without_links(self):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "p.html"
            r = run("--out", str(page), "combo", "1")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn(f"Swatch page: {page}", r.stdout)
            body = page.read_text()
            self.assertIn("#0093a5", body)
            self.assertNotIn("http", body)


if __name__ == "__main__":
    unittest.main()

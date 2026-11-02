import json
import subprocess
import sys
import unittest
from pathlib import Path

from engine import evaluate


def example():
    return json.loads(Path(__file__).with_name("example.json").read_text(encoding="utf-8"))


class AcceptanceTests(unittest.TestCase):
    def test_example_cli(self):
        proc = subprocess.run([sys.executable, "cli.py", "example.json"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), evaluate(example()))

    def test_additive_change_and_silent_loss(self):
        data = example()
        self.assertTrue(evaluate(data)["passed"])
        data["migration_sql"] = "UPDATE orders SET paid=0 WHERE id=2;"
        self.assertEqual(evaluate(data)["differences"], {"captured": [770, 230]})

    def test_attach_is_denied(self):
        data = example()
        data["migration_sql"] = "ATTACH ':memory:' AS outside;"
        self.assertFalse(evaluate(data)["passed"])

    def test_read_only_source_survives_destructive_trial(self):
        import tempfile
        import sqlite3
        from contextlib import closing
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.db"
            data = example()
            with closing(sqlite3.connect(path)) as db:
                db.executescript(data.pop("fixture_sql"))
            data.update(source=str(path), migration_sql="DROP TABLE orders;")
            initial = path.read_bytes()
            self.assertFalse(evaluate(data)["passed"])
            self.assertEqual(path.read_bytes(), initial)

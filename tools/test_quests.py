"""Regression checks for progression and the generated quest graph (stdlib only)."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import gen_quests as book


class QuestTests(unittest.TestCase):
    def setUp(self):
        self.chapters = book.build_chapters()
        self.by_key = {c.key: c for c in self.chapters}

    def test_book_has_valid_ids_and_acyclic_dependencies(self):
        book.validate(self.chapters)

    def test_every_trial_teaches_exactly_its_tier(self):
        for n in range(1, 11):
            chapter = next(c for c in self.chapters if c.key.startswith(f"phase_{n}_"))
            rewards = chapter.by_key["trial"]["rewards"]
            self.assertEqual([r["stage"] for r in rewards if r["type"] == "gamestage"], [f"ultimate_tier_{n}"])

    def test_late_joiner_can_use_gate_without_crafting_another(self):
        chapter = self.by_key["phase_9_way_back"]
        self.assertEqual(chapter.by_key["trial"]["dependencies"], [chapter.by_key["start"]["id"]])
        self.assertEqual(chapter.by_key["trial"]["tasks"][0]["stage"], "ultimate_return_gate")

    def test_gate_crafting_branch_does_not_block_chapter_completion(self):
        chapter = self.by_key["phase_9_way_back"]
        for key in ["head", "materials", "build"]:
            self.assertTrue(chapter.by_key[key]["optional"])

    def test_breath_is_available_before_dragon_dies(self):
        chapter = self.by_key["phase_10_dragon"]
        self.assertEqual(chapter.by_key["breath"]["dependencies"], [chapter.by_key["island"]["id"]])

    def test_creative_crossing_does_not_require_ship_parts(self):
        chapter = self.by_key["phase_10_dragon"]
        self.assertEqual(chapter.by_key["island"]["dependencies"], [chapter.by_key["start"]["id"]])

    def test_far_lands_remains_two_of_four(self):
        trial = self.by_key["phase_4_far_lands"].by_key["trial"]
        self.assertEqual(trial["min_required_dependencies"], 2)
        self.assertEqual(len(trial["dependencies"]), 4)

    def assert_invalid(self, change, message):
        change(self.by_key["welcome"])
        # Graph checks must work even on a fresh checkout without downloaded mods.
        with patch.object(book, "IDS_FILE", Path("/nonexistent/ultimate-pack-ids")):
            with self.assertRaisesRegex(ValueError, message):
                book.validate(self.chapters)

    def test_missing_dependency_is_rejected_without_id_cache(self):
        self.assert_invalid(lambda c: c.by_key["welcome"].update(dependencies=["0000000000000000"]), "missing dependency")

    def test_cycles_are_rejected(self):
        self.assert_invalid(lambda c: c.by_key["welcome"].update(dependencies=[c.by_key["together"]["id"]]), "cycle")

    def test_duplicate_ids_are_rejected(self):
        self.assert_invalid(lambda c: c.quests.append(c.quests[0]), "duplicate ID")

    def test_impossible_choice_is_rejected(self):
        self.assert_invalid(lambda c: c.by_key["together"].update(min_required_dependencies=2), "impossible dependency")

    def test_render_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a", Path(tmp) / "b"
            book.render(a)
            book.render(b)
            snapshot = lambda root: {p.relative_to(root): p.read_bytes() for p in root.rglob("*.snbt")}
            self.assertEqual(snapshot(a), snapshot(b))

    def test_invalid_edit_preserves_live_book(self):
        with tempfile.TemporaryDirectory() as tmp:
            live = Path(tmp) / "quests"
            live.mkdir()
            sentinel = live / "data.snbt"
            sentinel.write_text("existing player book")
            self.by_key["welcome"].by_key["welcome"]["dependencies"] = ["missing"]
            with patch.object(book, "OUT", live), patch.object(book, "build_chapters", return_value=self.chapters), patch("sys.argv", ["gen_quests.py"]):
                with self.assertRaises(ValueError):
                    book.main()
            self.assertEqual(sentinel.read_text(), "existing player book")

    def test_check_detects_stale_book_without_changing_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            live = Path(tmp) / "quests"
            live.mkdir()
            sentinel = live / "data.snbt"
            sentinel.write_text("stale")
            with patch.object(book, "OUT", live), patch("sys.argv", ["gen_quests.py", "--check"]):
                with self.assertRaisesRegex(SystemExit, "out of date"):
                    book.main()
            self.assertEqual(sentinel.read_text(), "stale")


if __name__ == "__main__":
    unittest.main()

import json
import os
import sys
import tempfile
import unittest

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import audio_settings as A


class SettingsFileTests(unittest.TestCase):
    def setUp(self):
        self.dir  = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "sub", "settings.json")

    def tearDown(self):
        self.dir.cleanup()

    def _write(self, text):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)

    def test_missing_file_gives_defaults(self):
        self.assertEqual(A.load_settings(self.path), A.DEFAULTS)

    def test_malformed_and_wrong_types_give_defaults(self):
        for text in ("", "{not json", "[]", "42", '{"audio": 5}', '{"audio": null}'):
            self._write(text)
            self.assertEqual(A.load_settings(self.path), A.DEFAULTS, text)

    def test_partial_and_invalid_values(self):
        self._write(json.dumps({"audio": {
            "master": 40, "music": "loud", "sfx": 250, "coin": -5, "extra": 1}}))
        self.assertEqual(A.load_settings(self.path),
                         {"master": 40, "music": 100, "sfx": 100, "coin": 0})

    def test_bool_nan_and_float(self):
        self._write('{"audio": {"master": true, "music": NaN, "sfx": 33.6, "coin": 50}}')
        self.assertEqual(A.load_settings(self.path),
                         {"master": 100, "music": 100, "sfx": 34, "coin": 50})

    def test_round_trip(self):
        vals = {"master": 10, "music": 20, "sfx": 30, "coin": 0}
        self.assertTrue(A.save_settings(vals, self.path))
        self.assertEqual(A.load_settings(self.path), vals)
        self.assertEqual([n for n in os.listdir(os.path.dirname(self.path))],
                         ["settings.json"])  # no leftover temp file

    def test_save_failure_does_not_raise(self):
        blocker = os.path.join(self.dir.name, "file")
        open(blocker, "w").close()
        self.assertFalse(A.save_settings(A.DEFAULTS, os.path.join(blocker, "x.json")))


class VolumeMathTests(unittest.TestCase):
    def test_full_equals_legacy_levels(self):
        e = A.effective_volumes(A.DEFAULTS)
        self.assertAlmostEqual(e["music"], 0.22)
        self.assertAlmostEqual(e["sfx"], 0.55)
        self.assertAlmostEqual(e["coin"], 0.55)

    def test_master_zero_silences_everything(self):
        e = A.effective_volumes({**A.DEFAULTS, "master": 0})
        self.assertEqual(e, {"music": 0.0, "sfx": 0.0, "coin": 0.0})

    def test_music_independent_of_sfx_and_coin(self):
        e = A.effective_volumes({"master": 100, "music": 50, "sfx": 0, "coin": 0})
        self.assertAlmostEqual(e["music"], 0.11)
        self.assertEqual(e["sfx"], 0.0)

    def test_coin_respects_master_and_sfx(self):
        e = A.effective_volumes({"master": 50, "music": 100, "sfx": 50, "coin": 50})
        self.assertAlmostEqual(e["coin"], 0.55 * 0.5 * 0.5 * 0.5)
        self.assertEqual(A.effective_volumes({"master": 100, "music": 100, "sfx": 0, "coin": 100})["coin"], 0.0)
        self.assertEqual(A.effective_volumes({"master": 100, "music": 100, "sfx": 100, "coin": 0})["coin"], 0.0)
        self.assertGreater(A.effective_volumes(A.DEFAULTS)["sfx"], 0)


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pygame
        try:
            import pygame.mixer  # noqa: F401  (absent in some pygame builds)
        except ImportError:
            raise unittest.SkipTest("pygame.mixer not available")
        import main
        pygame.init()
        cls.main = main

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "s.json")
        self.eng = self.main.SoundEngine(self.path)

    def tearDown(self):
        self.dir.cleanup()

    def test_defaults_applied(self):
        self.eng.play_coin()
        self.assertAlmostEqual(self.eng._cache["coin"].get_volume(), 0.55, places=1)
        self.assertAlmostEqual(self.eng._bg_sound.get_volume(), 0.22, places=1)

    def test_set_volume_updates_cached_and_future_sounds(self):
        self.eng.play_xp()                       # cached before change
        self.eng.set_volume("sfx", 0)
        self.eng.set_volume("music", 0)
        self.assertEqual(self.eng._cache["xp"].get_volume(), 0.0)
        self.assertEqual(self.eng._bg_sound.get_volume(), 0.0)
        self.eng.play_whip()                     # created after change
        self.assertEqual(self.eng._cache["whip"].get_volume(), 0.0)

    def test_coin_zero_only_silences_coin(self):
        self.eng.play_xp(); self.eng.play_coin()
        self.eng.set_volume("coin", 0)
        self.assertEqual(self.eng._cache["coin"].get_volume(), 0.0)
        self.assertGreater(self.eng._cache["xp"].get_volume(), 0.0)

    def test_mute_does_not_touch_volumes(self):
        self.eng.set_volume("master", 40)
        before = dict(self.eng.volumes)
        self.eng.play_xp()
        vol = self.eng._cache["xp"].get_volume()
        self.eng.toggle_mute()
        self.assertTrue(self.eng.muted)
        self.eng.set_volume("sfx", 60)           # slider while muted
        self.assertTrue(self.eng.muted)
        self.eng.toggle_mute()
        self.assertFalse(self.eng.muted)
        self.assertEqual(before["master"], self.eng.volumes["master"])
        self.assertNotEqual(vol, 0.0)

    def test_persistence_across_engines(self):
        self.eng.set_volume("music", 25)
        self.eng.set_volume("coin", 70)
        self.assertTrue(self.eng.save_volumes())
        again = self.main.SoundEngine(self.path)
        self.assertEqual(again.volumes["music"], 25)
        self.assertEqual(again.volumes["coin"], 70)
        self.assertAlmostEqual(again._bg_sound.get_volume(), 0.22 * 0.25, places=1)


if __name__ == "__main__":
    unittest.main()

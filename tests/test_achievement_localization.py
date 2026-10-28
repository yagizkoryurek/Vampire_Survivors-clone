import os
import sys
import unittest

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


class AchievementLocalizationTests(unittest.TestCase):
    def tearDown(self):
        main.LANG = "TR"

    def test_every_achievement_has_text_keys(self):
        self.assertEqual(len(main.ACHIEVEMENT_DEFS), 6)
        for d in main.ACHIEVEMENT_DEFS:
            self.assertIn(d.id, main.ACHIEVEMENT_TEXT_KEYS)
        self.assertEqual(set(main.ACHIEVEMENT_TEXT_KEYS), set(main.AchievementID))

    def test_all_keys_exist_in_both_languages(self):
        keys = ["ach_unlocked"]
        for title_key, desc_key in main.ACHIEVEMENT_TEXT_KEYS.values():
            keys += [title_key, desc_key]
        for lang in ("TR", "EN"):
            for k in keys:
                self.assertIn(k, main.STRINGS[lang], (lang, k))

    def test_translations_differ_between_languages(self):
        keys = ["ach_unlocked"]
        for title_key, desc_key in main.ACHIEVEMENT_TEXT_KEYS.values():
            keys += [title_key, desc_key]
        for k in keys:
            self.assertNotEqual(main.STRINGS["TR"][k], main.STRINGS["EN"][k], k)

    def test_text_follows_language_switch(self):
        title_key, desc_key = main.ACHIEVEMENT_TEXT_KEYS[main.AchievementID.FIRST_BLOOD]
        main.LANG = "EN"
        self.assertEqual(main.T("ach_unlocked"), "ACHIEVEMENT UNLOCKED!")
        self.assertEqual(main.T(title_key), "First Blood")
        self.assertEqual(main.T(desc_key), "Kill your first enemy")
        main.toggle_lang()
        self.assertEqual(main.T("ach_unlocked"), "BAŞARIM AÇILDI!")
        self.assertEqual(main.T(title_key), "İlk Kan")
        self.assertEqual(main.T(desc_key), "İlk düşmanı öldür")


if __name__ == "__main__":
    unittest.main()

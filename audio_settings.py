"""Ses ayarları: yükleme / kaydetme ve etkin ses seviyesi hesabı.

pygame'e bağımlı değildir; bu yüzden mixer açmadan test edilebilir.
Değerler 0-100 arası tam sayı yüzdelerdir.
"""
import json
import math
import os
import sys
import tempfile

KEYS     = ("master", "music", "sfx", "coin")
DEFAULTS = {"master": 100, "music": 100, "sfx": 100, "coin": 100}

BASE_MUSIC = 0.22   # eski sabit müzik seviyesi
BASE_SFX   = 0.55   # eski sabit efekt seviyesi

ENV_PATH = "VS_CLONE_SETTINGS"
VERSION  = 1


def clamp_percent(value, default=100):
    """Geçerli bir yüzdeyi 0..100 aralığına sıkıştırır; geçersizse default döner."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return default
    if isinstance(value, float) and not math.isfinite(value):
        return default
    return max(0, min(100, int(round(value))))


def sanitize(raw) -> dict:
    """Her anahtarı ayrı ayrı doğrular; bozuk/eksik olanlar varsayılana düşer."""
    raw = raw if isinstance(raw, dict) else {}
    return {k: clamp_percent(raw.get(k, DEFAULTS[k]), DEFAULTS[k]) for k in KEYS}


def effective_volumes(settings: dict) -> dict:
    """Pygame Sound.set_volume için 0..1 arası nihai çarpanlar.

    Coin sesi hem master hem de SFX seviyesine, ayrıca kendi seviyesine tabidir.
    Her kategori için 0% tam sessizlik verir.
    """
    s      = sanitize(settings)
    master = s["master"] / 100.0
    sfx    = master * s["sfx"] / 100.0
    return {
        "music": BASE_MUSIC * master * s["music"] / 100.0,
        "sfx":   BASE_SFX * sfx,
        "coin":  BASE_SFX * sfx * s["coin"] / 100.0,
    }


def default_settings_path() -> str:
    override = os.environ.get(ENV_PATH)
    if override:
        return override
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "VampireSurvivorsClone", "settings.json")


def load_settings(path=None) -> dict:
    """Dosya yoksa/bozuksa güvenle varsayılanları döner. Asla exception fırlatmaz."""
    try:
        with open(path or default_settings_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        return sanitize(data.get("audio") if isinstance(data, dict) else None)
    except Exception:
        return dict(DEFAULTS)


def save_settings(settings: dict, path=None) -> bool:
    """Atomik yazım (geçici dosya + os.replace). Başarıyı bool döner, asla fırlatmaz."""
    path = path or default_settings_path()
    tmp = None
    try:
        folder = os.path.dirname(path) or "."
        os.makedirs(folder, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"version": VERSION, "audio": sanitize(settings)}, f, indent=2)
        os.replace(tmp, path)
        return True
    except Exception:
        if tmp:
            try:
                os.remove(tmp)
            except OSError:
                pass
        return False

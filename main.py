"""
Vampire Survivors Clone - Python / Pygame
==========================================
Kontroller:
  WASD / Ok tuşları  -> hareket
  ESC                -> çıkış
  P                  -> duraklat

Özellikler:
  - Oyuncuya otomatik saldıran silah sistemi (whip, orb, aura)
  - Düşman spawn sistemi (wave tabanlı, artan zorluk)
  - XP & level-up sistemi + upgrade seçimi
  - Sağlık çubuğu, XP çubuğu, zamanlayıcı
  - Particle efektleri
  - Birden fazla düşman tipi
"""

import pygame
import math
import random
import sys
import array
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum, auto

# ---------------------------------------------------------------------------
# Dil sistemi (TR / EN)
# ---------------------------------------------------------------------------
LANG = "TR"  # Başlangıç dili

STRINGS = {
    "TR": {
        "title":         "Vampire Survivors Clone",
        "paused":        "DURAKLATILDI",
        "game_over":     "GAME OVER",
        "time":          "Süre",
        "level":         "Level",
        "kill":          "Kill",
        "wave":          "Dalga",
        "restart":       "[R] Yeniden Başla   [ESC] Çıkış",
        "controls":      "WASD: Hareket  P: Duraklat  L: Dil  M: Ses  ESC: Çıkış",
        "weapons":       "Kırbaç Lv{w}  Orb Lv{o}  Aura Lv{a}  Boomerang Lv{b}  Zırh {ar}  Regen {r}",
        "weapons_title": "Silahlar",
        "wpn_whip":      "Kırbaç",
        "wpn_orb":       "Orb",
        "wpn_aura":      "Aura",
        "wpn_boomerang": "Boomerang",
        "wpn_lightning": "Yıldırım",
        "wpn_ice":       "Buz",
        "wpn_armor":     "Zırh",
        "wpn_regen":     "Regen",
        "level_up":      "SEVİYE ATLADINIZ",
        "choose":        "Bir güçlendirme seçin",
        "click_hint":    "Tıkla veya [1/2/3]",
        "hp":            "HP",
        "lv":            "LV",
        "xp":            "XP",
        "muted":         "Ses: KAPALI",
        "unmuted":       "Ses: AÇIK",
        "lang_label":    "TR",
        "upgrade_names": {
            "MAX_HP":   "Maks Sağlık",
            "SPEED":    "Hız",
            "WHIP":     "Kırbaç Güçlendir",
            "ORB":      "Orb Güçlendir",
            "AURA":       "Aura Güçlendir",
            "BOOMERANG":  "Boomerang Güçlendir",
            "LIGHTNING_STAFF": "Yıldırım Değneği",
            "ICE_WAND": "Buz Değneği",
            "RECOVERY":   "Rejenerasyon",
            "ARMOR":    "Zırh",
        },
        "upgrade_descs": {
            "MAX_HP":   "+40 maks sağlık",
            "SPEED":    "+10% hareket hızı",
            "WHIP":     "Hasar & menzil artışı",
            "ORB":      "Yeni orb + hasar",
            "AURA":       "Alan & hasar artışı",
            "BOOMERANG":  "Hasar, hız & menzil artışı",
            "LIGHTNING_STAFF": "Hasar & alan artışı",
            "ICE_WAND": "Hasar & yavaşlatma artışı",
            "RECOVERY":   "+1 HP/sn kazanım",
            "ARMOR":    "Hasar azaltma",
        },
        # Menü / yeni özellik metinleri (TR)
        "menu_play":      "Oyuna Başla",
        "menu_campaign":  "Campaign",
        "menu_maps":      "Haritalar",
        "menu_settings":  "Ayarlar",
        "menu_chars":     "Karakterler",
        "menu_quit":      "Çıkış",
        "menu_back":      "Geri",
        "main_menu":      "Ana Menü",
        "campaign_title": "Campaign Mode",
        "map_title":      "Harita Seç",
        "map_start":      "Başlat",
        "map_difficulty": "Zorluk",
        "map_rewards":    "Ödüller",
        "map_unlock_default": "Açık",
        "map_unlock_survive": "5 dakika hayatta kal",
        "map_unlock_kills":   "500 kill yap",
        "campaign_level": "Level {n}",
        "target_wave":    "Target Wave {n}",
        "completed":      "TAMAMLANDI",
        "level_completed":"LEVEL COMPLETED",
        "next_level":     "Next Level",
        "menu_sound":     "Ses",
        "menu_sound_on":  "AÇIK",
        "menu_sound_off": "KAPALI",
        "menu_fullscreen":"Tam Ekran",
        "menu_fs_on":     "AÇIK",
        "menu_fs_off":    "KAPALI",
        "boss_fight":     "BOSS SAVAŞI!",
        "gold":           "Altın",
        "locked":         "KİLİTLİ",
        "buy":            "Satın Al",
        "owned":          "SAHİP",
        "not_enough":     "Yetersiz Altın",
        "selected":       "SEÇİLDİ",
        "restart":        "[R] Yeniden Başla   [ESC] Menü",
        "controls":       "WASD: Hareket  P: Duraklat  M: Ses  ESC: Menü",
        "char_names": {
            "warrior": "Savaşçı",
            "rogue":   "Haydut",
            "mage":    "Büyücü",
            "paladin": "Paladin",
        },
        "char_descs": {
            "warrior": "+40 HP, +2 Zırh",
            "rogue":   "+20% Hız, +1 HP/sn",
            "mage":    "Orb Lv2 başlar",
            "paladin": "+80 HP, +3 Zırh, -10% Hız",
        },
    },
    "EN": {
        "title":         "Vampire Survivors Clone",
        "paused":        "PAUSED",
        "game_over":     "GAME OVER",
        "time":          "Time",
        "level":         "Level",
        "kill":          "Kills",
        "wave":          "Wave",
        "restart":       "[R] Restart   [ESC] Quit",
        "controls":      "WASD: Move  P: Pause  L: Language  M: Sound  ESC: Quit",
        "weapons":       "Whip Lv{w}  Orb Lv{o}  Aura Lv{a}  Boomerang Lv{b}  Armor {ar}  Regen {r}",
        "weapons_title": "Weapons",
        "wpn_whip":      "Whip",
        "wpn_orb":       "Orb",
        "wpn_aura":      "Aura",
        "wpn_boomerang": "Boomerang",
        "wpn_lightning": "Lightning",
        "wpn_ice":       "Ice",
        "wpn_armor":     "Armor",
        "wpn_regen":     "Regen",
        "level_up":      "LEVEL UP",
        "choose":        "Choose an upgrade",
        "click_hint":    "Click or [1/2/3]",
        "hp":            "HP",
        "lv":            "LV",
        "xp":            "XP",
        "muted":         "Sound: OFF",
        "unmuted":       "Sound: ON",
        "lang_label":    "EN",
        "upgrade_names": {
            "MAX_HP":   "Max Health",
            "SPEED":    "Speed",
            "WHIP":     "Upgrade Whip",
            "ORB":      "Upgrade Orb",
            "AURA":       "Upgrade Aura",
            "BOOMERANG":  "Upgrade Boomerang",
            "LIGHTNING_STAFF": "Lightning Staff",
            "ICE_WAND": "Ice Wand",
            "RECOVERY":   "Regeneration",
            "ARMOR":    "Armor",
        },
        "upgrade_descs": {
            "MAX_HP":   "+40 max health",
            "SPEED":    "+10% move speed",
            "WHIP":     "Damage & range boost",
            "ORB":      "New orb + damage",
            "AURA":       "Area & damage boost",
            "BOOMERANG":  "Damage, speed & range boost",
            "LIGHTNING_STAFF": "Damage & area boost",
            "ICE_WAND": "Damage & slow boost",
            "RECOVERY":   "+1 HP/s recovery",
            "ARMOR":    "Reduce incoming damage",
        },
        # Menu / new features (EN)
        "menu_play":      "Play",
        "menu_campaign":  "Campaign",
        "menu_maps":      "Maps",
        "menu_settings":  "Settings",
        "menu_chars":     "Characters",
        "menu_quit":      "Quit",
        "menu_back":      "Back",
        "main_menu":      "Main Menu",
        "campaign_title": "Campaign Mode",
        "map_title":      "Select Map",
        "map_start":      "Start",
        "map_difficulty": "Difficulty",
        "map_rewards":    "Rewards",
        "map_unlock_default": "Unlocked",
        "map_unlock_survive": "Survive 5 minutes",
        "map_unlock_kills":   "Reach 500 kills",
        "campaign_level": "Level {n}",
        "target_wave":    "Target Wave {n}",
        "completed":      "COMPLETED",
        "level_completed":"LEVEL COMPLETED",
        "next_level":     "Next Level",
        "menu_sound":     "Sound",
        "menu_sound_on":  "ON",
        "menu_sound_off": "OFF",
        "menu_fullscreen":"Fullscreen",
        "menu_fs_on":     "ON",
        "menu_fs_off":    "OFF",
        "boss_fight":     "BOSS FIGHT!",
        "gold":           "Gold",
        "locked":         "LOCKED",
        "buy":            "Buy",
        "owned":          "OWNED",
        "not_enough":     "Not Enough Gold",
        "selected":       "SELECTED",
        "restart":        "[R] Restart   [ESC] Menu",
        "controls":       "WASD: Move  P: Pause  M: Sound  ESC: Menu",
        "char_names": {
            "warrior": "Warrior",
            "rogue":   "Rogue",
            "mage":    "Mage",
            "paladin": "Paladin",
        },
        "char_descs": {
            "warrior": "+40 HP, +2 Armor",
            "rogue":   "+20% Speed, +1 HP/s",
            "mage":    "Starts with Orb Lv2",
            "paladin": "+80 HP, +3 Armor, -10% Speed",
        },
    },
}

def T(key, **kwargs):
    """Mevcut dilde string döndürür."""
    s = STRINGS[LANG].get(key, key)
    if kwargs:
        s = s.format(**kwargs)
    return s

def toggle_lang():
    global LANG
    LANG = "EN" if LANG == "TR" else "TR"

# ---------------------------------------------------------------------------
# Ses motoru (prosedürel — harici dosya gerektirmez)
# ---------------------------------------------------------------------------
class SoundEngine:
    SR = 44100

    def __init__(self):
        pygame.mixer.pre_init(self.SR, -16, 1, 512)
        pygame.mixer.init()
        self.muted   = False
        self._cache: dict = {}
        self._bg_channel: Optional[pygame.mixer.Channel] = None
        self._start_bg()

    # --- Sinyal üreticiler ---
    def _sine_buf(self, freq, dur, vol=0.45, attack=0.01, decay_exp=1.0):
        n   = int(self.SR * dur)
        buf = array.array('h')
        for i in range(n):
            t   = i / self.SR
            env = min(t / attack, 1.0) * max(0.0, 1.0 - (t / dur) ** decay_exp)
            s   = int(vol * env * 32767 * math.sin(2 * math.pi * freq * t))
            buf.append(s)
        return bytes(buf)

    def _sweep_buf(self, f0, f1, dur, vol=0.4):
        n   = int(self.SR * dur)
        buf = array.array('h')
        ph  = 0.0
        for i in range(n):
            t    = i / self.SR
            env  = max(0.0, 1.0 - t / dur)
            freq = f0 + (f1 - f0) * (t / dur)
            ph  += 2 * math.pi * freq / self.SR
            s    = int(vol * env * 32767 * math.sin(ph))
            buf.append(s)
        return bytes(buf)

    def _noise_buf(self, dur, vol=0.35):
        n   = int(self.SR * dur)
        buf = array.array('h')
        for i in range(n):
            env = max(0.0, 1.0 - i / n)
            s   = int(vol * env * 32767 * (random.random() * 2 - 1))
            buf.append(s)
        return bytes(buf)

    def _make(self, key, fn):
        if key not in self._cache:
            data = fn()
            snd  = pygame.mixer.Sound(buffer=data)
            snd.set_volume(0.55)
            self._cache[key] = snd
        return self._cache[key]

    def _play(self, snd):
        if not self.muted:
            snd.play()

    # --- Oyun sesleri ---
    def play_hit(self):
        self._play(self._make('hit',
            lambda: self._noise_buf(0.08, 0.3)))

    def play_whip(self):
        self._play(self._make('whip',
            lambda: self._sweep_buf(600, 150, 0.14, 0.5)))

    def play_orb(self):
        self._play(self._make('orb',
            lambda: self._sine_buf(520, 0.12, 0.35)))

    def play_aura(self):
        self._play(self._make('aura',
            lambda: self._sine_buf(180, 0.18, 0.25, decay_exp=2)))

    def play_xp(self):
        self._play(self._make('xp',
            lambda: self._sweep_buf(400, 900, 0.12, 0.3)))

    def play_levelup(self):
        self._play(self._make('lvlup',
            lambda: self._sweep_buf(500, 1400, 0.35, 0.5)))

    def play_damage(self):
        self._play(self._make('dmg',
            lambda: self._sweep_buf(200, 80, 0.18, 0.45)))

    def play_lightning(self):
        self._play(self._make('lightning',
            lambda: self._sweep_buf(1400, 300, 0.12, 0.45)))

    def play_ice(self):
        self._play(self._make('ice',
            lambda: self._sine_buf(1700, 0.08, 0.35, attack=0.005, decay_exp=1.5)))

    def play_death(self):
        self._play(self._make('death',
            lambda: self._noise_buf(0.5, 0.55)))

    # --- Arka plan müziği (prosedürel loop) ---
    def _build_bg(self):
        """Ambient drone + ritim: tamamen kod ile üretilir."""
        dur   = 4.0
        n     = int(self.SR * dur)
        buf   = array.array('h')
        notes = [110, 138.6, 164.8, 130.8]  # Am pentatonik
        for i in range(n):
            t    = i / self.SR
            beat = t * 2  # 120 BPM
            # Drone katmanı
            drone = (math.sin(2*math.pi*55*t) * 0.18 +
                     math.sin(2*math.pi*110*t) * 0.12 +
                     math.sin(2*math.pi*220*t) * 0.06)
            # Melodi
            note_idx = int(beat * 2) % len(notes)
            freq     = notes[note_idx]
            env_m    = 0.5 + 0.5 * math.sin(beat * math.pi)
            melody   = math.sin(2*math.pi*freq*t) * 0.10 * env_m
            # Ritim (düşük frekans pulse)
            kick = math.sin(2*math.pi*80*t) * math.exp(-8 * (beat % 1)) * 0.15
            val  = int((drone + melody + kick) * 32767 * 0.6)
            val  = max(-32767, min(32767, val))
            buf.append(val)
        return bytes(buf)

    def _start_bg(self):
        try:
            data = self._build_bg()
            snd  = pygame.mixer.Sound(buffer=data)
            snd.set_volume(0.22)
            self._bg_channel = snd.play(loops=-1)
        except Exception:
            self._bg_channel = None

    def toggle_mute(self):
        self.muted = not self.muted
        if self._bg_channel:
            if self.muted:
                pygame.mixer.pause()
            else:
                pygame.mixer.unpause()

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TILE = 64
WORLD_W, WORLD_H = 4000, 4000

# Renkler
C_BG          = (12, 10, 18)
C_GRID        = (22, 20, 32)
C_PLAYER      = (120, 220, 255)
C_PLAYER_DARK = (60, 140, 180)
C_HP_BG       = (60, 20, 20)
C_HP          = (220, 60, 60)
C_XP_BG       = (20, 40, 20)
C_XP          = (80, 220, 100)
C_UI_BG       = (15, 14, 25, 200)
C_WHITE       = (255, 255, 255)
C_YELLOW      = (255, 230, 80)
C_ORANGE      = (255, 140, 40)
C_PURPLE      = (180, 80, 255)
C_CYAN        = (60, 230, 255)
C_RED         = (255, 60, 60)
C_GREEN       = (80, 220, 100)
C_BOOMERANG   = (100, 255, 180)
C_LIGHTNING   = (255, 245, 120)
C_ICE         = (150, 220, 255)

# ---------------------------------------------------------------------------
# Yardımcı
# ---------------------------------------------------------------------------
def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def norm(dx, dy):
    d = math.hypot(dx, dy)
    if d == 0:
        return 0.0, 0.0
    return dx / d, dy / d

def angle_to(src, dst):
    return math.atan2(dst[1] - src[1], dst[0] - src[0])

# ---------------------------------------------------------------------------
# Particle
# ---------------------------------------------------------------------------
class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size')

    def __init__(self, x, y, color, speed=2.0, size=4, life=30):
        self.x, self.y = float(x), float(y)
        angle = random.uniform(0, math.tau)
        s = random.uniform(speed * 0.4, speed)
        self.vx = math.cos(angle) * s
        self.vy = math.sin(angle) * s
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.92
        self.vy *= 0.92
        self.life -= 1
        return self.life > 0

    def draw(self, surf, cam_x, cam_y):
        t = self.life / self.max_life
        alpha = int(t * 255)
        r, g, b = self.color
        s = max(1, int(self.size * t))
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if -s < sx < SCREEN_W + s and -s < sy < SCREEN_H + s:
            pygame.draw.circle(surf, (r, g, b), (sx, sy), s)

# ---------------------------------------------------------------------------
# DamageNumber
# ---------------------------------------------------------------------------
class DamageNumber:
    def __init__(self, x, y, value, color=C_YELLOW):
        self.x, self.y = float(x), float(y)
        self.vy = -1.5
        self.life = 50
        self.value = value
        self.color = color

    def update(self):
        self.y += self.vy
        self.vy *= 0.95
        self.life -= 1
        return self.life > 0

    def draw(self, surf, cam_x, cam_y, font):
        alpha = clamp(int(self.life / 50 * 255), 0, 255)
        text = font.render(str(self.value), True, self.color)
        text.set_alpha(alpha)
        surf.blit(text, (int(self.x - cam_x) - text.get_width() // 2,
                         int(self.y - cam_y)))

# ---------------------------------------------------------------------------
# Silah sistemi
# ---------------------------------------------------------------------------
class Projectile:
    def __init__(self, x, y, angle, speed, damage, lifetime, color, size=6,
                 pierce=1):
        self.x, self.y = float(x), float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.life = lifetime
        self.color = color
        self.size = size
        self.pierce = pierce
        self.hit_set: set = set()
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.alive = False

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if -20 < sx < SCREEN_W + 20 and -20 < sy < SCREEN_H + 20:
            # Parlama efekti
            glow = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            r, g, b = self.color
            pygame.draw.circle(glow, (r, g, b, 60), (self.size * 2, self.size * 2),
                                self.size * 2)
            surf.blit(glow, (sx - self.size * 2, sy - self.size * 2))
            pygame.draw.circle(surf, self.color, (sx, sy), self.size)
            pygame.draw.circle(surf, C_WHITE, (sx, sy), self.size // 2)


class AuraWeapon:
    """Oyuncunun etrafındaki hasar alanı."""
    def __init__(self):
        self.radius = 80
        self.damage = 8
        self.cooldown = 0
        self.tick = 40
        self.level = 1

    def upgrade(self):
        self.level += 1
        self.radius += 15
        self.damage += 4
        self.tick = max(20, self.tick - 5)

    def update(self, player, enemies, particles, damage_numbers, sfx=None):
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = self.tick
            px, py = player.x, player.y
            hit_any = False
            for e in enemies:
                if dist((px, py), (e.x, e.y)) < self.radius + e.radius:
                    e.take_damage(self.damage)
                    damage_numbers.append(DamageNumber(e.x, e.y, self.damage, C_PURPLE))
                    hit_any = True
                    for _ in range(4):
                        particles.append(Particle(e.x, e.y, C_PURPLE, speed=2))
            if hit_any and sfx:
                sfx.play_aura()

    def draw(self, surf, cam_x, cam_y, player, tick):
        px = int(player.x - cam_x)
        py = int(player.y - cam_y)
        pulse = 0.85 + 0.15 * math.sin(tick * 0.15)
        r = int(self.radius * pulse)
        aura_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (180, 80, 255, 30), (r + 1, r + 1), r)
        pygame.draw.circle(aura_surf, (180, 80, 255, 80), (r + 1, r + 1), r, 2)
        surf.blit(aura_surf, (px - r - 1, py - r - 1))


class Boomerang:
    def __init__(self, x, y, angle, speed, damage, max_range):
        self.x, self.y = float(x), float(y)
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.max_range = max_range
        self.traveled = 0.0
        self.returning = False
        self.hit_set: set = set()
        self.alive = True
        self.color = C_BOOMERANG

    def update(self, player):
        if self.returning:
            self.angle = angle_to((self.x, self.y), (player.x, player.y))
            d = dist((self.x, self.y), (player.x, player.y))
            if d < 15:
                self.alive = False
                return
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        if not self.returning:
            self.traveled += self.speed
            if self.traveled >= self.max_range:
                self.returning = True
                self.hit_set.clear()

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if -20 < sx < SCREEN_W + 20 and -20 < sy < SCREEN_H + 20:
            spin = pygame.time.get_ticks() * 0.018
            size = 12
            pts = []
            for i in range(3):
                a = spin + (math.tau / 3) * i
                pts.append((sx + int(math.cos(a) * size),
                            sy + int(math.sin(a) * size)))
            glow = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.color, 40), (size * 2, size * 2), size * 2)
            surf.blit(glow, (sx - size * 2, sy - size * 2))
            pygame.draw.polygon(surf, self.color, pts)
            pygame.draw.polygon(surf, C_WHITE, pts, 1)


class BoomerangWeapon:
    def __init__(self):
        self.damage = 22
        self.speed = 5.0
        self.range = 250
        self.cooldown = 0
        self.tick = 90
        self.level = 1
        self.boomerangs: List[Boomerang] = []

    def upgrade(self):
        self.level += 1
        self.damage += 8
        self.speed += 0.5
        self.range += 30
        self.tick = max(45, self.tick - 8)

    def update(self, player, enemies, particles, damage_numbers, sfx=None):
        for b in self.boomerangs:
            b.update(player)
            if b.alive:
                for e in enemies:
                    if e.alive and id(e) not in b.hit_set:
                        if dist((b.x, b.y), (e.x, e.y)) < 16 + e.radius:
                            e.take_damage(b.damage)
                            b.hit_set.add(id(e))
                            damage_numbers.append(DamageNumber(e.x, e.y, b.damage, b.color))
                            for _ in range(5):
                                particles.append(Particle(b.x, b.y, b.color, speed=2.5))
                            if sfx:
                                sfx.play_hit()
        self.boomerangs = [b for b in self.boomerangs if b.alive]

        self.cooldown -= 1
        if self.cooldown <= 0:
            target = None
            best = self.range + 100
            for e in enemies:
                d = dist((player.x, player.y), (e.x, e.y))
                if d < best:
                    best = d
                    target = e
            if target:
                self.cooldown = self.tick
                a = angle_to((player.x, player.y), (target.x, target.y))
                self.boomerangs.append(Boomerang(
                    player.x, player.y, a, self.speed, self.damage, self.range))
            else:
                self.cooldown = self.tick // 2

    def draw(self, surf, cam_x, cam_y, player):
        for b in self.boomerangs:
            b.draw(surf, cam_x, cam_y)


class WhipWeapon:
    """Periyodik olarak en yakın düşmana vuran kırbaç."""
    def __init__(self):
        self.damage = 25
        self.cooldown = 0
        self.tick = 80
        self.range = 200
        self.level = 1
        self.angle = 0.0
        self.flash = 0

    def upgrade(self):
        self.level += 1
        self.damage += 12
        self.range += 30
        self.tick = max(40, self.tick - 8)

    def update(self, player, enemies, particles, damage_numbers, sfx=None):
        self.cooldown -= 1
        if self.flash > 0:
            self.flash -= 1
        if self.cooldown <= 0:
            target = None
            best = self.range
            for e in enemies:
                d = dist((player.x, player.y), (e.x, e.y))
                if d < best:
                    best = d
                    target = e
            if target:
                self.cooldown = self.tick
                self.angle = angle_to((player.x, player.y), (target.x, target.y))
                self.flash = 12
                if sfx:
                    sfx.play_whip()
                # Kırbaç aralıktaki tüm düşmanlara vurur
                for e in enemies:
                    a = angle_to((player.x, player.y), (e.x, e.y))
                    if dist((player.x, player.y), (e.x, e.y)) < self.range:
                        da = abs(math.atan2(math.sin(a - self.angle),
                                            math.cos(a - self.angle)))
                        if da < 0.4:
                            e.take_damage(self.damage)
                            damage_numbers.append(
                                DamageNumber(e.x, e.y, self.damage, C_ORANGE))
                            for _ in range(6):
                                particles.append(
                                    Particle(e.x, e.y, C_ORANGE, speed=3))
            else:
                self.cooldown = self.tick // 2

    def draw(self, surf, cam_x, cam_y, player):
        if self.flash > 0:
            px, py = player.x, player.y
            r = self.range
            ex = px + math.cos(self.angle) * r
            ey = py + math.sin(self.angle) * r
            t = self.flash / 12
            alpha = int(t * 200)
            for i in range(3):
                spread = (i - 1) * 0.15
                a = self.angle + spread
                lx = px + math.cos(a) * r
                ly = py + math.sin(a) * r
                pygame.draw.line(surf, (*C_ORANGE, alpha),
                                 (int(px - cam_x), int(py - cam_y)),
                                 (int(lx - cam_x), int(ly - cam_y)),
                                 max(1, int(3 * t)))


class OrbWeapon:
    """Oyuncunun etrafında dönen küreler."""
    def __init__(self):
        self.damage = 18
        self.cooldown = 0
        self.tick = 1
        self.count = 3
        self.radius = 100
        self.speed = 0.04  # rad/frame
        self.angle = 0.0
        self.level = 1
        self.hit_cooldowns: dict = {}

    def upgrade(self):
        self.level += 1
        self.count += 1
        self.damage += 6
        self.radius += 10

    def update(self, player, enemies, particles, damage_numbers, sfx=None):
        self.angle += self.speed
        # Her orb için çarpışma
        for i in range(self.count):
            a = self.angle + (math.tau / self.count) * i
            ox = player.x + math.cos(a) * self.radius
            oy = player.y + math.sin(a) * self.radius
            for e in enemies:
                eid = id(e)
                if eid not in self.hit_cooldowns:
                    self.hit_cooldowns[eid] = 0
                if self.hit_cooldowns[eid] > 0:
                    self.hit_cooldowns[eid] -= 1
                    continue
                if dist((ox, oy), (e.x, e.y)) < 18 + e.radius:
                    e.take_damage(self.damage)
                    damage_numbers.append(DamageNumber(e.x, e.y, self.damage, C_CYAN))
                    self.hit_cooldowns[eid] = 30
                    if sfx:
                        sfx.play_orb()
                    for _ in range(5):
                        particles.append(Particle(ox, oy, C_CYAN, speed=2.5))
        # Ölü düşmanların kaydını temizle
        live = {id(e) for e in enemies}
        self.hit_cooldowns = {k: v for k, v in self.hit_cooldowns.items()
                               if k in live}

    def draw(self, surf, cam_x, cam_y, player, tick):
        for i in range(self.count):
            a = self.angle + (math.tau / self.count) * i
            ox = int(player.x + math.cos(a) * self.radius - cam_x)
            oy = int(player.y + math.sin(a) * self.radius - cam_y)
            # Parlama
            glow = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(glow, (60, 230, 255, 50), (20, 20), 18)
            surf.blit(glow, (ox - 20, oy - 20))
            pygame.draw.circle(surf, C_CYAN, (ox, oy), 10)
            pygame.draw.circle(surf, C_WHITE, (ox, oy), 4)

class LightningBolt:
    WARN_FRAMES = 18
    STRIKE_FLASH_FRAMES = 10

    def __init__(self, tx, ty, damage, aoe_radius, index=0):
        self.tx, self.ty = float(tx), float(ty)
        self.damage = damage
        self.aoe_radius = aoe_radius
        self.index = index
        self.timer = self.WARN_FRAMES
        self.struck = False
        self.flash_timer = 0
        self.alive = True

    def _strike(self, enemies, particles, damage_numbers, sfx):
        self.struck = True
        self.flash_timer = self.STRIKE_FLASH_FRAMES
        for e in enemies:
            if not e.alive:
                continue
            if dist((self.tx, self.ty), (e.x, e.y)) < self.aoe_radius + e.radius:
                e.take_damage(self.damage)
                damage_numbers.append(DamageNumber(e.x, e.y, self.damage, C_LIGHTNING))
                for _ in range(4):
                    particles.append(Particle(e.x, e.y, C_LIGHTNING, speed=3))
        if sfx:
            sfx.play_lightning()

    def update(self, player, enemies, particles, damage_numbers, sfx=None):
        if not self.struck:
            self.timer -= 1
            if self.timer <= 0:
                self._strike(enemies, particles, damage_numbers, sfx)
        else:
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.alive = False

    def draw(self, surf, cam_x, cam_y, tick):
        sx = int(self.tx - cam_x)
        sy = int(self.ty - cam_y)
        if not (-60 < sx < SCREEN_W + 60 and -60 < sy < SCREEN_H + 60):
            return
        if not self.struck:
            t = self.timer / self.WARN_FRAMES
            r = max(4, int(self.aoe_radius * (0.55 + 0.45 * t)))
            ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*C_LIGHTNING, 140), (r + 2, r + 2), r, 3)
            surf.blit(ring, (sx - r - 2, sy - r - 2))
        else:
            t = self.flash_timer / self.STRIKE_FLASH_FRAMES
            alpha = int(220 * t)
            pygame.draw.line(surf, (*C_LIGHTNING, alpha), (sx, sy - 160), (sx, sy),
                             max(2, int(4 * t)))
            flash = pygame.Surface((self.aoe_radius * 2, self.aoe_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash, (*C_LIGHTNING, int(90 * t)),
                               (self.aoe_radius, self.aoe_radius), self.aoe_radius)
            surf.blit(flash, (sx - self.aoe_radius, sy - self.aoe_radius))
            pygame.draw.circle(surf, C_WHITE, (sx, sy), max(2, int(6 * t)))


class LightningStaffWeapon:
    def __init__(self):
        self.level = 1
        self.damage = 28
        self.cooldown = 0
        self.tick = 110
        self.aoe_radius = 55
        self.count = 1
        self.detection_range = 480
        self.active: List[LightningBolt] = []

    def upgrade(self):
        self.level += 1
        self.damage += 10
        self.tick = max(55, self.tick - 12)
        self.aoe_radius += 6
        if self.level >= 4 and self.count < 2:
            self.count = 2

    def _pick_targets(self, player, enemies):
        alive = [e for e in enemies
                 if e.alive and dist((player.x, player.y), (e.x, e.y)) <= self.detection_range]
        alive.sort(key=lambda e: dist((player.x, player.y), (e.x, e.y)))
        return alive[:self.count]

    def update(self, player, enemies, particles, damage_numbers, sfx=None):
        self.cooldown -= 1
        if self.cooldown <= 0:
            targets = self._pick_targets(player, enemies)
            if targets:
                self.cooldown = self.tick
                for i, target in enumerate(targets):
                    self.active.append(
                        LightningBolt(target.x, target.y, self.damage, self.aoe_radius, index=i))
            else:
                self.cooldown = self.tick // 2

        for bolt in self.active:
            bolt.update(player, enemies, particles, damage_numbers, sfx)
        self.active = [bolt for bolt in self.active if bolt.alive]

    def draw(self, surf, cam_x, cam_y, tick):
        for bolt in self.active:
            bolt.draw(surf, cam_x, cam_y, tick)


class IceShard:
    def __init__(self, px, py, angle, damage, speed, slow_duration, slow_factor,
                 freeze_duration, lifetime=90, size=6):
        self.x, self.y = float(px), float(py)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.slow_duration = slow_duration
        self.slow_factor = slow_factor
        self.freeze_duration = freeze_duration
        self.life = lifetime
        self.size = size
        self.alive = True

    def update(self, player, enemies, particles, damage_numbers, sfx=None):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.alive = False
            return

        for e in enemies:
            if not e.alive:
                continue
            if dist((self.x, self.y), (e.x, e.y)) < self.size + e.radius:
                e.take_damage(self.damage)
                e.apply_slow(self.slow_duration, self.slow_factor)
                if self.freeze_duration > 0:
                    e.apply_freeze(self.freeze_duration)
                damage_numbers.append(DamageNumber(e.x, e.y, self.damage, C_ICE))
                for _ in range(5):
                    particles.append(Particle(e.x, e.y, C_ICE, speed=2.5))
                if sfx:
                    sfx.play_ice()
                self.alive = False
                return

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if -20 < sx < SCREEN_W + 20 and -20 < sy < SCREEN_H + 20:
            glow = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*C_ICE, 60), (self.size * 2, self.size * 2),
                                self.size * 2)
            surf.blit(glow, (sx - self.size * 2, sy - self.size * 2))
            angle = math.atan2(self.vy, self.vx)
            pts = []
            for off, r in ((0, self.size * 1.4), (math.tau * 0.42, self.size * 0.6),
                           (math.pi, self.size * 0.9), (-math.tau * 0.42, self.size * 0.6)):
                a = angle + off
                pts.append((sx + math.cos(a) * r, sy + math.sin(a) * r))
            pygame.draw.polygon(surf, C_ICE, pts)
            pygame.draw.polygon(surf, C_WHITE, pts, 1)


class IceWandWeapon:
    ICE_FREEZE_LEVEL = 5

    def __init__(self):
        self.level = 1
        self.damage = 16
        self.cooldown = 0
        self.tick = 95
        self.proj_speed = 7.0
        self.slow_duration = 90
        self.slow_factor = 0.55
        self.freeze_duration = 0
        self.detection_range = 450
        self.active: List[IceShard] = []

    def upgrade(self):
        self.level += 1
        self.damage += 7
        self.tick = max(45, self.tick - 9)
        self.proj_speed += 0.5
        self.slow_duration += 12
        self.slow_factor = max(0.25, self.slow_factor - 0.04)
        if self.level >= self.ICE_FREEZE_LEVEL:
            self.freeze_duration = min(45, 15 + (self.level - self.ICE_FREEZE_LEVEL) * 6)

    def _pick_target(self, player, enemies):
        target = None
        best = self.detection_range
        for e in enemies:
            if not e.alive:
                continue
            d = dist((player.x, player.y), (e.x, e.y))
            if d <= best:
                best = d
                target = e
        return target

    def update(self, player, enemies, particles, damage_numbers, sfx=None):
        self.cooldown -= 1
        if self.cooldown <= 0:
            target = self._pick_target(player, enemies)
            if target:
                self.cooldown = self.tick
                a = angle_to((player.x, player.y), (target.x, target.y))
                self.active.append(IceShard(
                    player.x, player.y, a, self.damage, self.proj_speed,
                    self.slow_duration, self.slow_factor, self.freeze_duration))
            else:
                self.cooldown = self.tick // 2

        for shard in self.active:
            shard.update(player, enemies, particles, damage_numbers, sfx)
        self.active = [shard for shard in self.active if shard.alive]

    def draw(self, surf, cam_x, cam_y, tick):
        for shard in self.active:
            shard.draw(surf, cam_x, cam_y)


# ---------------------------------------------------------------------------
# Upgrade seçenekleri
# ---------------------------------------------------------------------------
class UpgradeType(Enum):
    MAX_HP      = auto()
    SPEED       = auto()
    WHIP        = auto()
    ORB         = auto()
    AURA        = auto()
    BOOMERANG   = auto()
    LIGHTNING_STAFF = auto()
    ICE_WAND    = auto()
    RECOVERY    = auto()
    ARMOR       = auto()

UPGRADE_COLORS = {
    UpgradeType.MAX_HP:   C_RED,
    UpgradeType.SPEED:    C_YELLOW,
    UpgradeType.WHIP:     C_ORANGE,
    UpgradeType.ORB:      C_CYAN,
    UpgradeType.AURA:     C_PURPLE,
    UpgradeType.BOOMERANG: C_CYAN,
    UpgradeType.LIGHTNING_STAFF: C_LIGHTNING,
    UpgradeType.ICE_WAND: C_ICE,
    UpgradeType.RECOVERY: C_GREEN,
    UpgradeType.ARMOR:    C_WHITE,
}

UPGRADE_KEYS = {
    UpgradeType.MAX_HP:   "MAX_HP",
    UpgradeType.SPEED:    "SPEED",
    UpgradeType.WHIP:     "WHIP",
    UpgradeType.ORB:      "ORB",
    UpgradeType.AURA:     "AURA",
    UpgradeType.BOOMERANG: "BOOMERANG",
    UpgradeType.LIGHTNING_STAFF: "LIGHTNING_STAFF",
    UpgradeType.ICE_WAND: "ICE_WAND",
    UpgradeType.RECOVERY: "RECOVERY",
    UpgradeType.ARMOR:    "ARMOR",
}

def get_upgrade_def(ut):
    key   = UPGRADE_KEYS[ut]
    name  = STRINGS[LANG]["upgrade_names"][key]
    desc  = STRINGS[LANG]["upgrade_descs"][key]
    color = UPGRADE_COLORS[ut]
    return name, desc, color

# ---------------------------------------------------------------------------
# Düşman tipleri
# ---------------------------------------------------------------------------
class EnemyType(Enum):
    BASIC  = auto()
    FAST   = auto()
    TANK   = auto()
    RANGED = auto()

ENEMY_DEFS = {
    EnemyType.BASIC:  dict(hp=40,  speed=1.2, damage=8,  xp=5,  radius=14, color=(200, 60, 60)),
    EnemyType.FAST:   dict(hp=20,  speed=2.4, damage=5,  xp=8,  radius=10, color=(255, 120, 40)),
    EnemyType.TANK:   dict(hp=200, speed=0.7, damage=20, xp=20, radius=22, color=(120, 60, 200)),
    EnemyType.RANGED: dict(hp=35,  speed=0.9, damage=10, xp=12, radius=13, color=(60, 200, 120)),
}

class Enemy:
    def __init__(self, x, y, etype: EnemyType, wave: int):
        self.x, self.y = float(x), float(y)
        self.etype = etype
        d = ENEMY_DEFS[etype]
        scale = 1 + wave * 0.08
        self.max_hp = int(d['hp'] * scale)
        self.hp     = self.max_hp
        self.speed  = d['speed']
        self.damage = int(d['damage'] * scale)
        self.xp     = d['xp']
        self.radius = d['radius']
        self.color  = d['color']
        self.alive  = True
        self.hit_flash = 0
        self.shoot_cd  = random.randint(60, 120)  # RANGED için

        # Knockback
        self.kbx = 0.0
        self.kby = 0.0

        # Ranged için mermi oluşturmak amacıyla referans tutulur
        self.pending_shots: List[Projectile] = []

        self.slow_timer = 0
        self.slow_factor = 1.0
        self.frozen_timer = 0

    def apply_slow(self, duration: int, factor: float) -> None:
        self.slow_timer = max(self.slow_timer, duration)
        self.slow_factor = min(self.slow_factor, factor)

    def apply_freeze(self, duration: int) -> None:
        self.frozen_timer = max(self.frozen_timer, duration)

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = 8
        self.kbx += random.uniform(-2, 2)
        self.kby += random.uniform(-2, 2)
        if self.hp <= 0:
            self.alive = False

    def update(self, player, projectiles_out):
        # Knockback sönümleme
        self.x += self.kbx
        self.y += self.kby
        self.kbx *= 0.8
        self.kby *= 0.8

        if self.frozen_timer > 0:
            self.frozen_timer -= 1
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        # Oyuncuya doğru git
        effective_speed = 0.0 if self.frozen_timer > 0 else self.speed * self.slow_factor
        dx = player.x - self.x
        dy = player.y - self.y
        d = math.hypot(dx, dy)
        if d > 0 and effective_speed > 0:
            self.x += (dx / d) * effective_speed
            self.y += (dy / d) * effective_speed

        # Dünya sınırları
        self.x = clamp(self.x, 0, WORLD_W)
        self.y = clamp(self.y, 0, WORLD_H)

        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Ranged saldırı
        if self.etype == EnemyType.RANGED:
            self.shoot_cd -= 1
            if self.shoot_cd <= 0:
                self.shoot_cd = random.randint(90, 150)
                a = angle_to((self.x, self.y), (player.x, player.y))
                proj = Projectile(self.x, self.y, a, speed=3.5,
                                  damage=self.damage, lifetime=80,
                                  color=(60, 200, 120), size=7)
                proj.is_enemy = True
                projectiles_out.append(proj)

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        r = self.radius
        if sx + r < 0 or sx - r > SCREEN_W or sy + r < 0 or sy - r > SCREEN_H:
            return

        if self.hit_flash > 0:
            color = C_WHITE
        elif self.frozen_timer > 0:
            color = C_ICE
        elif self.slow_timer > 0:
            color = tuple(int(c * 0.7 + 130 * 0.3) for c in self.color)
        else:
            color = self.color
        pygame.draw.circle(surf, color, (sx, sy), r)
        if self.frozen_timer > 0:
            pygame.draw.circle(surf, (200, 240, 255), (sx, sy), r + 2, 2)
        # Tank için dışında halka
        if self.etype == EnemyType.TANK:
            pygame.draw.circle(surf, C_WHITE, (sx, sy), r + 3, 2)
        # HP çubuğu
        bar_w = r * 2
        bar_h = 4
        bx = sx - r
        by = sy - r - 8
        pygame.draw.rect(surf, C_HP_BG, (bx, by, bar_w, bar_h))
        fill = int(bar_w * self.hp / self.max_hp)
        pygame.draw.rect(surf, C_HP, (bx, by, fill, bar_h))

# ---------------------------------------------------------------------------
# XP Drop
# ---------------------------------------------------------------------------
class XPGem:
    def __init__(self, x, y, value):
        self.x, self.y = float(x), float(y)
        self.value = value
        self.alive = True
        self.bob = random.uniform(0, math.tau)

    def update(self, player):
        self.bob += 0.08
        # Oyuncuya yakınsa çekilir
        d = dist((self.x, self.y), (player.x, player.y))
        if d < player.pickup_radius:
            dx, dy = norm(player.x - self.x, player.y - self.y)
            self.x += dx * 6
            self.y += dy * 6
        if d < player.radius + 10:
            self.alive = False
            return self.value
        return 0

    def draw(self, surf, cam_x, cam_y, tick):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y + math.sin(self.bob) * 3)
        if -10 < sx < SCREEN_W + 10 and -10 < sy < SCREEN_H + 10:
            pygame.draw.polygon(surf, C_GREEN,
                                [(sx, sy - 8), (sx + 6, sy), (sx, sy + 8), (sx - 6, sy)])
            pygame.draw.polygon(surf, C_WHITE,
                                [(sx, sy - 8), (sx + 6, sy), (sx, sy + 8), (sx - 6, sy)],
                                1)

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player:
    def __init__(self, x, y, character_id="warrior", color=C_PLAYER):
        self.x, self.y = float(x), float(y)
        self.character_id = character_id
        self.color = color
        self.dark_color = tuple(max(0, int(c * 0.5)) for c in color)
        self.base_speed = 3.0
        self.speed_mult = 1.0
        self.radius = 16
        self.pickup_radius = 80

        self.max_hp = 120
        self.hp = self.max_hp
        self.recovery = 0  # HP/sn
        self.armor = 0
        self.recovery_acc = 0.0

        self.invincible = 0  # hasar sonrası kısa dokunulmazlık
        self.hit_flash = 0

        self.xp = 0
        self.level = 1
        self.xp_needed = 10

        # Silahlar
        self.whip     = WhipWeapon()
        self.orb      = OrbWeapon()
        self.aura     = AuraWeapon()
        self.boomerang = BoomerangWeapon()

        self.angle = 0.0  # görsel yön

    @property
    def speed(self):
        return self.base_speed * self.speed_mult

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            self.level += 1
            self.xp_needed = int(self.xp_needed * 1.3)
            leveled = True
        return leveled

    def take_damage(self, amount):
        if self.invincible > 0:
            return
        dmg = max(1, amount - self.armor)
        self.hp -= dmg
        self.invincible = 45
        self.hit_flash = 10

    def update(self, keys, dt):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        nx, ny = norm(dx, dy)
        self.x = clamp(self.x + nx * self.speed, 0, WORLD_W)
        self.y = clamp(self.y + ny * self.speed, 0, WORLD_H)

        if nx != 0 or ny != 0:
            self.angle = math.atan2(ny, nx)

        if self.invincible > 0:
            self.invincible -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Rejenerasyon
        if self.recovery > 0:
            self.recovery_acc += self.recovery / FPS
            while self.recovery_acc >= 1.0:
                self.hp = min(self.max_hp, self.hp + 1)
                self.recovery_acc -= 1.0

    def draw(self, surf, cam_x, cam_y, tick):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        r = self.radius

        # Gölge
        shadow = pygame.Surface((r * 2 + 4, r + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80), (0, 0, r * 2 + 4, r + 4))
        surf.blit(shadow, (sx - r - 2, sy + r - 2))

        color = C_WHITE if self.hit_flash > 0 else self.color
        # Yanıp sönme (dokunulmazlık)
        if self.invincible > 0 and (tick // 4) % 2 == 0:
            color = (200, 200, 200)

        cid = self.character_id

        # Character silhouettes
        if cid == "rogue":
            body_r = r - 3
            hood = [(sx, sy - r - 6), (sx - r, sy - 3), (sx - body_r, sy + 8),
                    (sx, sy + r - 1), (sx + body_r, sy + 8), (sx + r, sy - 3)]
            pygame.draw.polygon(surf, self.dark_color, hood)
            pygame.draw.polygon(surf, color, [(sx, sy - r - 2), (sx - r + 4, sy - 2),
                                              (sx, sy + r - 5), (sx + r - 4, sy - 2)])
            pygame.draw.rect(surf, (15, 12, 25), (sx - 9, sy - 4, 18, 6), border_radius=3)
        elif cid == "mage":
            robe = [(sx, sy - r + 3), (sx - r + 1, sy + r), (sx + r - 1, sy + r)]
            pygame.draw.polygon(surf, self.dark_color, robe)
            pygame.draw.polygon(surf, color, [(sx, sy - r + 6), (sx - r + 5, sy + r - 2),
                                              (sx + r - 5, sy + r - 2)])
            pygame.draw.polygon(surf, self.dark_color,
                                [(sx - 11, sy - r + 1), (sx + 11, sy - r + 1), (sx, sy - r - 21)])
            pygame.draw.polygon(surf, color,
                                [(sx - 7, sy - r), (sx + 7, sy - r), (sx, sy - r - 15)])
            pygame.draw.ellipse(surf, self.dark_color, (sx - 15, sy - r - 2, 30, 7))
        elif cid in ("paladin", "tank"):
            pygame.draw.ellipse(surf, self.dark_color, (sx - r - 7, sy - 5, (r + 7) * 2, r + 16))
            pygame.draw.rect(surf, self.dark_color, (sx - r - 6, sy - 3, (r + 6) * 2, r + 13),
                             border_radius=7)
            pygame.draw.circle(surf, color, (sx, sy), r - 2)
            pygame.draw.rect(surf, (220, 235, 230), (sx - 3, sy - r + 2, 6, r + 9), border_radius=2)
        else:
            pygame.draw.ellipse(surf, self.dark_color, (sx - r - 3, sy - r + 1, (r + 3) * 2, r * 2))
            pygame.draw.circle(surf, self.dark_color, (sx, sy), r)
            pygame.draw.circle(surf, color, (sx, sy), r - 3)
            pygame.draw.arc(surf, (220, 240, 255), (sx - r + 4, sy - r + 4, (r - 4) * 2, (r - 4) * 2),
                            math.radians(210), math.radians(330), 2)

        # Göz
        ex = sx + int(math.cos(self.angle) * 6)
        ey = sy + int(math.sin(self.angle) * 6)
        pygame.draw.circle(surf, C_WHITE, (ex, ey), 4)
        pygame.draw.circle(surf, (10, 10, 30), (ex, ey), 2)

# ---------------------------------------------------------------------------
# Upgrade UI
# ---------------------------------------------------------------------------
class UpgradeScreen:
    def __init__(self, available):
        self.choices = random.sample(available, min(3, len(available)))
        self.hovered = None
        self.font_big  = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_med  = pygame.font.SysFont("segoeui", 20)
        self.font_sm   = pygame.font.SysFont("segoeui", 16)

    def draw(self, surf):
        # Karartma
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        title = self.font_big.render(T("level_up"), True, C_YELLOW)
        surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))
        sub = self.font_med.render(T("choose"), True, (180, 180, 220))
        surf.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 100))

        card_w, card_h = 280, 160
        gap = 30
        total_w = len(self.choices) * card_w + (len(self.choices) - 1) * gap
        start_x = SCREEN_W // 2 - total_w // 2
        cy = SCREEN_H // 2 - card_h // 2 + 20

        mx, my = pygame.mouse.get_pos()
        self.hovered = None

        for i, ut in enumerate(self.choices):
            cx = start_x + i * (card_w + gap)
            hovering = cx <= mx <= cx + card_w and cy <= my <= cy + card_h
            if hovering:
                self.hovered = i

            name, desc, color = get_upgrade_def(ut)

            # Kart arka planı
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            bg_alpha = 220 if hovering else 170
            card_surf.fill((*C_UI_BG[:3], bg_alpha))
            surf.blit(card_surf, (cx, cy))

            border_color = color if hovering else (80, 80, 120)
            border_w = 3 if hovering else 1
            pygame.draw.rect(surf, border_color, (cx, cy, card_w, card_h), border_w,
                             border_radius=8)

            # İkon + isim
            name_surf = self.font_big.render(name, True, color)
            surf.blit(name_surf,
                      (cx + card_w // 2 - name_surf.get_width() // 2, cy + 20))

            desc_surf = self.font_med.render(desc, True, (200, 200, 230))
            surf.blit(desc_surf,
                      (cx + card_w // 2 - desc_surf.get_width() // 2, cy + 80))

            if hovering:
                hint = self.font_sm.render(T("click_hint"), True, (160, 160, 200))
                surf.blit(hint,
                          (cx + card_w // 2 - hint.get_width() // 2, cy + 120))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered is not None:
                return self.choices[self.hovered]
        if event.type == pygame.KEYDOWN:
            num_map = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}
            if event.key in num_map:
                idx = num_map[event.key]
                if idx < len(self.choices):
                    return self.choices[idx]
        return None

# ---------------------------------------------------------------------------
# Spawn yöneticisi
# ---------------------------------------------------------------------------
class SpawnManager:
    def __init__(self, map_def=None):
        self.timer = 0
        self.wave = 0
        self.wave_timer = 0
        self.base_rate = 120  # frame/spawn
        self.horde_cd = 0
        self.map_def = map_def or MAP_DEFS[0]

    def update(self, player, enemies, tick):
        self.timer += 1
        self.wave_timer += 1

        # Her 30 saniyede bir wave artar
        wave = tick // (30 * FPS)
        self.wave = wave

        rate = max(20, int((self.base_rate - wave * 5) * self.map_def.get("spawn_rate_mult", 1.0)))

        if self.timer >= rate:
            self.timer = 0
            self._spawn(player, enemies, wave)

        # Her 60 saniyede bir horde
        if tick > 0 and tick % (60 * FPS) == 0:
            horde_count = int((20 + wave * 5) * self.map_def.get("horde_mult", 1.0))
            for _ in range(horde_count):
                self._spawn(player, enemies, wave)

    def _spawn(self, player, enemies, wave):
        # Ekranın dışında spawn et
        margin = 200
        side = random.randint(0, 3)
        if side == 0:
            x = player.x + random.uniform(-SCREEN_W // 2 - margin, SCREEN_W // 2 + margin)
            y = player.y - SCREEN_H // 2 - margin
        elif side == 1:
            x = player.x + SCREEN_W // 2 + margin
            y = player.y + random.uniform(-SCREEN_H // 2 - margin, SCREEN_H // 2 + margin)
        elif side == 2:
            x = player.x + random.uniform(-SCREEN_W // 2 - margin, SCREEN_W // 2 + margin)
            y = player.y + SCREEN_H // 2 + margin
        else:
            x = player.x - SCREEN_W // 2 - margin
            y = player.y + random.uniform(-SCREEN_H // 2 - margin, SCREEN_H // 2 + margin)

        x = clamp(x, 0, WORLD_W)
        y = clamp(y, 0, WORLD_H)

        # Tipe göre olasılık
        r = random.random()
        if wave < 2 or r < 0.50:
            etype = EnemyType.BASIC
        elif r < 0.70:
            etype = EnemyType.FAST
        elif r < 0.85:
            etype = EnemyType.RANGED
        else:
            etype = EnemyType.TANK

        enemies.append(Enemy(x, y, etype, wave))

# ---------------------------------------------------------------------------
# Altın drop (XPGem ile aynı pattern)
# ---------------------------------------------------------------------------
class GoldCoin:
    """Düşmanlardan ve bosslardan düşen altın."""
    def __init__(self, x, y, value):
        self.x, self.y = float(x), float(y)
        self.value  = value
        self.alive  = True
        self.bob    = random.uniform(0, math.tau)

    def update(self, player):
        self.bob += 0.09
        d = dist((self.x, self.y), (player.x, player.y))
        if d < player.pickup_radius:
            nx, ny = norm(player.x - self.x, player.y - self.y)
            self.x += nx * 6
            self.y += ny * 6
        if d < player.radius + 10:
            self.alive = False
            return self.value
        return 0

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y + math.sin(self.bob) * 3)
        if -12 < sx < SCREEN_W + 12 and -12 < sy < SCREEN_H + 12:
            pygame.draw.circle(surf, C_YELLOW, (sx, sy), 7)
            pygame.draw.circle(surf, (200, 160, 0), (sx, sy), 7, 2)
            pygame.draw.circle(surf, (255, 255, 180), (sx - 2, sy - 2), 2)


# ---------------------------------------------------------------------------
# Boss düşman
# ---------------------------------------------------------------------------
class Boss:
    """
    Her BOSS_INTERVAL saniyede bir spawn olur.
    Normal Enemy'den bağımsız sınıf — kendi draw/update/take_damage'i var.
    """
    BASE_HP     = 1200
    BASE_DAMAGE = 30
    BASE_SPEED  = 0.9
    RADIUS      = 38
    COLOR       = (220, 30, 180)
    RING_COLOR  = (255, 80, 220)
    XP_REWARD   = 120
    GOLD_REWARD = 80   # öldüğünde düşecek altın miktarı

    def __init__(self, x, y, wave):
        self.x, self.y  = float(x), float(y)
        scale           = 1 + wave * 0.12
        self.max_hp     = int(self.BASE_HP * scale)
        self.hp         = self.max_hp
        self.damage     = int(self.BASE_DAMAGE * scale)
        self.speed      = self.BASE_SPEED
        self.radius     = self.RADIUS
        self.alive      = True
        self.hit_flash  = 0
        self.shoot_cd   = 90          # mermi cooldown
        self.kbx = self.kby = 0.0
        self.angle      = 0.0         # görsel spin
        self.slow_timer = 0
        self.slow_factor = 1.0
        self.frozen_timer = 0

    def apply_slow(self, duration: int, factor: float) -> None:
        self.slow_timer = max(self.slow_timer, duration)
        self.slow_factor = min(self.slow_factor, factor)

    def apply_freeze(self, duration: int) -> None:
        self.frozen_timer = max(self.frozen_timer, duration)

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = 8
        self.kbx += random.uniform(-1.5, 1.5)
        self.kby += random.uniform(-1.5, 1.5)
        if self.hp <= 0:
            self.alive = False

    def update(self, player, projectiles_out):
        self.angle += 0.03
        self.x += self.kbx;  self.kbx *= 0.8
        self.y += self.kby;  self.kby *= 0.8
        if self.frozen_timer > 0:
            self.frozen_timer -= 1
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        effective_speed = 0.0 if self.frozen_timer > 0 else self.speed * self.slow_factor
        dx = player.x - self.x
        dy = player.y - self.y
        d  = math.hypot(dx, dy)
        if d > 0 and effective_speed > 0:
            self.x += (dx / d) * effective_speed
            self.y += (dy / d) * effective_speed
        self.x = clamp(self.x, 0, WORLD_W)
        self.y = clamp(self.y, 0, WORLD_H)
        if self.hit_flash > 0:
            self.hit_flash -= 1
        # Spiral ateş: 4 yönde mermi
        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            self.shoot_cd = 55
            for i in range(4):
                a = self.angle + (math.tau / 4) * i
                proj = Projectile(self.x, self.y, a, speed=3.8,
                                  damage=self.damage, lifetime=100,
                                  color=(255, 60, 220), size=9)
                proj.is_enemy = True
                projectiles_out.append(proj)

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        r  = self.radius
        if sx + r < 0 or sx - r > SCREEN_W or sy + r < 0 or sy - r > SCREEN_H:
            return
        # Dış halka (dönen)
        ring_surf = pygame.Surface((r * 3 + 4, r * 3 + 4), pygame.SRCALPHA)
        rc = r + 2
        for i in range(8):
            a  = self.angle + (math.tau / 8) * i
            px = rc + int(math.cos(a) * (r + 8))
            py = rc + int(math.sin(a) * (r + 8))
            pygame.draw.circle(ring_surf, (*self.RING_COLOR, 180), (px, py), 5)
        surf.blit(ring_surf, (sx - rc, sy - rc))
        # Gövde
        if self.hit_flash > 0:
            color = C_WHITE
        elif self.frozen_timer > 0:
            color = C_ICE
        elif self.slow_timer > 0:
            color = tuple(int(c * 0.7 + 130 * 0.3) for c in self.COLOR)
        else:
            color = self.COLOR
        pygame.draw.circle(surf, (120, 10, 100), (sx, sy), r)
        pygame.draw.circle(surf, color, (sx, sy), r - 4)
        pygame.draw.circle(surf, self.RING_COLOR, (sx, sy), r - 4, 3)
        if self.frozen_timer > 0:
            pygame.draw.circle(surf, (200, 240, 255), (sx, sy), r + 2, 2)
        # HP çubuğu (geniş)
        bw = r * 3
        bx = sx - r - r // 2
        by = sy - r - 14
        pygame.draw.rect(surf, C_HP_BG, (bx, by, bw, 8))
        fill = int(bw * self.hp / self.max_hp)
        pygame.draw.rect(surf, (255, 40, 200), (bx, by, fill, 8))
        pygame.draw.rect(surf, self.RING_COLOR, (bx, by, bw, 8), 1)
        # "BOSS" etiketi
        font = pygame.font.SysFont("segoeui", 13, bold=True)
        lbl  = font.render("BOSS", True, self.RING_COLOR)
        surf.blit(lbl, (sx - lbl.get_width() // 2, by - 14))


# ---------------------------------------------------------------------------
# Sandık sistemi
# ---------------------------------------------------------------------------
class ChestDrop(Enum):
    GOLD   = auto()
    DRONE  = auto()
    TURRET = auto()

class Chest:
    """
    Haritada rastgele konumlarda belirir.
    Oyuncu yaklaşıp üzerine yürüyünce açılır; içinden altın, drone veya taret çıkar.
    Açıldıktan sonra CHEST_RESPAWN_TICKS frame içinde yeni konumda yeniden doğar.
    """
    RADIUS           = 18
    RESPAWN_TICKS    = 1800   # 30 sn @ 60 fps
    COLOR_CLOSED     = (180, 140, 40)
    COLOR_OPEN       = (100, 80, 20)

    def __init__(self):
        self._place()
        self.open        = False
        self.respawn_cd  = 0
        self.bob         = random.uniform(0, math.tau)

    def _place(self):
        """Oyuncudan bağımsız rastgele dünya konumu."""
        self.x = float(random.randint(200, WORLD_W - 200))
        self.y = float(random.randint(200, WORLD_H - 200))

    def update(self, player):
        """
        Dönüş değeri: ChestDrop enum (ödül tipi) ya da None.
        """
        self.bob += 0.07
        if self.open:
            self.respawn_cd -= 1
            if self.respawn_cd <= 0:
                self._place()
                self.open = False
            return None
        # Açılma kontrolü
        if dist((self.x, self.y), (player.x, player.y)) < self.RADIUS + player.radius:
            self.open       = True
            self.respawn_cd = self.RESPAWN_TICKS
            # Ödül seçimi: %60 altın, %25 drone, %15 taret
            r = random.random()
            if r < 0.60:
                return ChestDrop.GOLD
            elif r < 0.85:
                return ChestDrop.DRONE
            else:
                return ChestDrop.TURRET
        return None

    def draw(self, surf, cam_x, cam_y):
        if self.open:
            return
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y + math.sin(self.bob) * 3)
        if sx + 24 < 0 or sx - 24 > SCREEN_W or sy + 24 < 0 or sy - 24 > SCREEN_H:
            return
        # Sandık gövdesi
        pygame.draw.rect(surf, self.COLOR_CLOSED, (sx - 14, sy - 10, 28, 20), border_radius=4)
        pygame.draw.rect(surf, (220, 180, 60), (sx - 14, sy - 10, 28, 20), 2, border_radius=4)
        # Kapak
        pygame.draw.rect(surf, (200, 160, 50), (sx - 14, sy - 14, 28, 8), border_radius=3)
        pygame.draw.rect(surf, (240, 200, 80), (sx - 14, sy - 14, 28, 8), 1, border_radius=3)
        # Kilit
        pygame.draw.rect(surf, (60, 50, 20), (sx - 3, sy - 4, 6, 6), border_radius=2)


# ---------------------------------------------------------------------------
# Drone (oyuncuyu takip eder, düşmanlara ateş eder)
# ---------------------------------------------------------------------------
class Drone:
    """
    Sandıktan elde edilen drone.
    Oyuncunun etrafında yörüngede döner, en yakın düşmana otomatik ateş eder.
    Birden fazla drone olabilir (liste ile yönetilir).
    """
    ORBIT_RADIUS = 70
    ORBIT_SPEED  = 0.045   # rad/frame
    SHOOT_CD     = 45
    DAMAGE       = 20
    RANGE        = 300
    COLOR        = (80, 200, 255)

    def __init__(self, index=0):
        self.index    = index          # birden fazla drone için açı offseti
        self.angle    = (math.tau / 4) * index
        self.shoot_cd = random.randint(0, self.SHOOT_CD)

    def update(self, player, enemies, projectiles_out, damage_numbers, particles):
        self.angle += self.ORBIT_SPEED
        # Pozisyon
        ox = player.x + math.cos(self.angle) * self.ORBIT_RADIUS
        oy = player.y + math.sin(self.angle) * self.ORBIT_RADIUS

        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            # En yakın düşmanı bul
            target = None
            best_d = self.RANGE
            for e in enemies:
                d = dist((ox, oy), (e.x, e.y))
                if d < best_d:
                    best_d = d
                    target = e
            if target:
                self.shoot_cd = self.SHOOT_CD
                a = angle_to((ox, oy), (target.x, target.y))
                proj = Projectile(ox, oy, a, speed=7, damage=self.DAMAGE,
                                  lifetime=50, color=self.COLOR, size=5)
                projectiles_out.append(proj)
                for _ in range(3):
                    particles.append(Particle(ox, oy, self.COLOR, speed=2, life=15))
            else:
                self.shoot_cd = self.SHOOT_CD // 2

    def draw(self, surf, cam_x, cam_y, player):
        ox = int(player.x + math.cos(self.angle) * self.ORBIT_RADIUS - cam_x)
        oy = int(player.y + math.sin(self.angle) * self.ORBIT_RADIUS - cam_y)
        # Bağlantı çizgisi
        px = int(player.x - cam_x)
        py = int(player.y - cam_y)
        pygame.draw.line(surf, (*self.COLOR, 60), (px, py), (ox, oy), 1)
        # Drone gövdesi
        glow = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.COLOR, 50), (14, 14), 12)
        surf.blit(glow, (ox - 14, oy - 14))
        pygame.draw.circle(surf, self.COLOR, (ox, oy), 7)
        pygame.draw.circle(surf, C_WHITE, (ox, oy), 3)


# ---------------------------------------------------------------------------
# Taret (yerleştirilen sabit kule)
# ---------------------------------------------------------------------------
class Turret:
    """
    Sandıktan elde edilen taret.
    Oyuncunun bulunduğu yere yerleştirilir, sabit kalır, menzilindeki düşmanlara ateş eder.
    Ömrü LIFETIME frame'dir.
    """
    RANGE    = 220
    SHOOT_CD = 35
    DAMAGE   = 28
    LIFETIME = 1800   # 30 sn
    RADIUS   = 14
    COLOR    = (255, 180, 40)

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.shoot_cd  = 0
        self.life      = self.LIFETIME
        self.alive     = True
        self.angle     = 0.0   # görselde dönen top

    def update(self, enemies, projectiles_out, damage_numbers, particles):
        self.life -= 1
        if self.life <= 0:
            self.alive = False
            return

        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            target = None
            best_d = self.RANGE
            for e in enemies:
                d = dist((self.x, self.y), (e.x, e.y))
                if d < best_d:
                    best_d = d
                    target = e
            if target:
                self.shoot_cd = self.SHOOT_CD
                self.angle    = angle_to((self.x, self.y), (target.x, target.y))
                a             = self.angle
                proj = Projectile(self.x, self.y, a, speed=8, damage=self.DAMAGE,
                                  lifetime=40, color=self.COLOR, size=5)
                projectiles_out.append(proj)
                for _ in range(3):
                    particles.append(Particle(self.x, self.y, self.COLOR, speed=2, life=12))
            else:
                self.shoot_cd = self.SHOOT_CD // 2

    def draw(self, surf, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        if sx + 20 < 0 or sx - 20 > SCREEN_W or sy + 20 < 0 or sy - 20 > SCREEN_H:
            return
        # Menzil dairesi (soluk)
        range_surf = pygame.Surface((self.RANGE * 2 + 2, self.RANGE * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surf, (*self.COLOR, 18),
                           (self.RANGE + 1, self.RANGE + 1), self.RANGE)
        pygame.draw.circle(range_surf, (*self.COLOR, 50),
                           (self.RANGE + 1, self.RANGE + 1), self.RANGE, 1)
        surf.blit(range_surf, (sx - self.RANGE - 1, sy - self.RANGE - 1))
        # Taban
        pygame.draw.circle(surf, (80, 60, 20), (sx, sy), self.RADIUS)
        pygame.draw.circle(surf, self.COLOR, (sx, sy), self.RADIUS - 2)
        # Namlu
        ex = sx + int(math.cos(self.angle) * (self.RADIUS + 8))
        ey = sy + int(math.sin(self.angle) * (self.RADIUS + 8))
        pygame.draw.line(surf, (255, 220, 80), (sx, sy), (ex, ey), 4)
        # Ömür çubuğu
        lf = self.life / self.LIFETIME
        bw = self.RADIUS * 2
        pygame.draw.rect(surf, (60, 40, 0), (sx - self.RADIUS, sy + self.RADIUS + 4, bw, 4))
        pygame.draw.rect(surf, self.COLOR,  (sx - self.RADIUS, sy + self.RADIUS + 4,
                                             int(bw * lf), 4))


# ---------------------------------------------------------------------------
# Karakter tanımları
# ---------------------------------------------------------------------------
# Her karakter: isim, açıklama, maliyet (altın), başlangıç stat modifierleri
CHARACTER_DEFS = [
    {
        "id":    "warrior",
        "name":  "Savaşçı",
        "desc":  "+40 HP, +2 Zırh",
        "cost":  0,             # Başlangıç karakteri — ücretsiz
        "color": (120, 220, 255),
        "mods":  {"max_hp": 40, "armor": 2},
    },
    {
        "id":    "rogue",
        "name":  "Haydut",
        "desc":  "+20% Hız, +1 HP/sn",
        "cost":  150,
        "color": (255, 180, 60),
        "mods":  {"speed_mult": 0.2, "recovery": 1},
    },
    {
        "id":    "mage",
        "name":  "Büyücü",
        "desc":  "Orb Lv2 başlar",
        "cost":  200,
        "color": (180, 80, 255),
        "mods":  {"orb_level": 1},
    },
    {
        "id":    "paladin",
        "name":  "Paladin",
        "desc":  "+80 HP, +3 Zırh, -10% Hız",
        "cost":  300,
        "color": (80, 220, 180),
        "mods":  {"max_hp": 80, "armor": 3, "speed_mult": -0.1},
    },
]


# ---------------------------------------------------------------------------
# Haritalar: menü, önizleme, kilit durumu ve oynanış modifierleri
# ---------------------------------------------------------------------------
MAP_DEFS = [
    {
        "id": "meadow",
        "name": "Meadow",
        "desc": "Balanced open field.",
        "difficulty": "Normal",
        "unlock_key": "map_unlock_default",
        "bg": C_BG,
        "grid": C_GRID,
        "preview": (28, 24, 42),
        "spawn_rate_mult": 1.0,
        "horde_mult": 1.0,
        "boss_interval_mult": 1.0,
        "xp_mult": 1.0,
        "gold_mult": 1.0,
    },
    {
        "id": "library",
        "name": "Library",
        "desc": "Dense corridors with faster pressure and better XP.",
        "difficulty": "Hard",
        "unlock_key": "map_unlock_survive",
        "bg": (10, 12, 22),
        "grid": (42, 36, 62),
        "preview": (36, 28, 58),
        "spawn_rate_mult": 0.88,
        "horde_mult": 1.25,
        "boss_interval_mult": 1.0,
        "xp_mult": 1.15,
        "gold_mult": 1.05,
    },
    {
        "id": "crypt",
        "name": "Crypt",
        "desc": "Riskier elites and stronger gold rewards.",
        "difficulty": "Expert",
        "unlock_key": "map_unlock_kills",
        "bg": (8, 14, 13),
        "grid": (26, 48, 42),
        "preview": (24, 54, 44),
        "spawn_rate_mult": 1.08,
        "horde_mult": 0.9,
        "boss_interval_mult": 1.2,
        "xp_mult": 0.95,
        "gold_mult": 1.35,
    },
]


def get_map_def(map_id):
    for mdef in MAP_DEFS:
        if mdef["id"] == map_id:
            return mdef
    return MAP_DEFS[0]

# ---------------------------------------------------------------------------
# Kalıcı veri (altın + açık karakterler — oyun oturumu boyunca saklanır)
# ---------------------------------------------------------------------------
class SaveData:
    """
    Tek instance (game.save). Altın, açık karakterler ve campaign ilerlemesini tutar.
    Dosya sistemi yok — hafızada saklanır, menüye dönünce korunur.
    """
    def __init__(self):
        self.total_gold    = 0
        self.unlocked_ids  = {"warrior"}   # Başlangıç karakteri açık
        self.selected_id   = "warrior"
        self.unlocked_map_ids = {"meadow"}
        self.selected_map_id = "meadow"
        self.best_survival_seconds = 0
        self.best_kills = 0
        self.campaign_unlocked_level = 1

    def unlock(self, char_id, cost):
        if self.total_gold >= cost:
            self.total_gold   -= cost
            self.unlocked_ids.add(char_id)
            return True
        return False

    def complete_campaign_level(self, level):
        if 1 <= level <= 30:
            self.campaign_unlocked_level = max(
                self.campaign_unlocked_level,
                min(30, level + 1)
            )

    def record_run(self, elapsed_seconds, kills):
        self.best_survival_seconds = max(self.best_survival_seconds, elapsed_seconds)
        self.best_kills = max(self.best_kills, kills)
        if self.best_survival_seconds >= 300:
            self.unlocked_map_ids.add("library")
        if self.best_kills >= 500:
            self.unlocked_map_ids.add("crypt")


def campaign_target_wave(level):
    return 10 + (level - 1) * 2


# ---------------------------------------------------------------------------
# Menü: ortak Button bileşeni
# ---------------------------------------------------------------------------
class Button:
    CLR_NORMAL   = (30, 28, 50)
    CLR_HOVER    = (60, 55, 100)
    CLR_BORDER   = (80, 75, 140)
    CLR_BORDER_H = (140, 120, 255)
    CLR_TEXT     = (200, 195, 240)
    CLR_TEXT_H   = (255, 255, 255)

    def __init__(self, x, y, w, h, label, font):
        self.base_rect = pygame.Rect(x, y, w, h)
        self.label     = label
        self.font      = font
        self.hovered   = False
        self._hover_t  = 0.0

    def update(self, mx, my):
        self.hovered = self.base_rect.collidepoint(mx, my)
        target       = 1.0 if self.hovered else 0.0
        self._hover_t += (target - self._hover_t) * 0.18

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.base_rect.collidepoint(event.pos))

    def draw(self, surf):
        t      = self._hover_t
        expand = int(t * 3)
        rect   = self.base_rect.inflate(expand * 2, expand * 2)
        bg     = tuple(int(a + (b - a) * t) for a, b in zip(self.CLR_NORMAL, self.CLR_HOVER))
        border = tuple(int(a + (b - a) * t) for a, b in zip(self.CLR_BORDER, self.CLR_BORDER_H))
        txtclr = tuple(int(a + (b - a) * t) for a, b in zip(self.CLR_TEXT,   self.CLR_TEXT_H))
        if t > 0.05:
            sh = pygame.Surface((rect.w + 8, rect.h + 8), pygame.SRCALPHA)
            pygame.draw.rect(sh, (0, 0, 0, int(80 * t)), sh.get_rect(), border_radius=10)
            surf.blit(sh, (rect.x - 4, rect.y + 4))
        pygame.draw.rect(surf, bg, rect, border_radius=8)
        pygame.draw.rect(surf, border, rect, 2, border_radius=8)
        ts = self.font.render(self.label, True, txtclr)
        surf.blit(ts, ts.get_rect(center=rect.center))


# ---------------------------------------------------------------------------
# GameState
# ---------------------------------------------------------------------------
class GameState(Enum):
    MENU       = auto()
    MAP_SELECT = auto()
    CAMPAIGN   = auto()
    SETTINGS   = auto()
    CHARACTERS = auto()
    PLAYING    = auto()


# ---------------------------------------------------------------------------
# Ana Menü
# ---------------------------------------------------------------------------
class MainMenu:
    BTN_W, BTN_H, BTN_GAP = 300, 52, 16

    def __init__(self, sfx):
        self.sfx  = sfx
        self.tick = 0
        self.font_title = pygame.font.SysFont("segoeui", 62, bold=True)
        self.font_sub   = pygame.font.SysFont("segoeui", 20)
        self.font_btn   = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_ver   = pygame.font.SysFont("segoeui", 13)
        self._bg_parts  = [self._new_p() for _ in range(55)]
        self._build_buttons()

    def _build_buttons(self):
        cx     = SCREEN_W // 2 - self.BTN_W // 2
        step   = self.BTN_H + self.BTN_GAP
        start  = SCREEN_H // 2 - 45
        self.buttons = {
            "play":     Button(cx, start,           self.BTN_W, self.BTN_H, T("menu_play"),     self.font_btn),
            "campaign": Button(cx, start + step,    self.BTN_W, self.BTN_H, T("menu_campaign"), self.font_btn),
            "chars":    Button(cx, start + step*2,  self.BTN_W, self.BTN_H, T("menu_chars"),    self.font_btn),
            "settings": Button(cx, start + step*3,  self.BTN_W, self.BTN_H, T("menu_settings"), self.font_btn),
            "quit":     Button(cx, start + step*4,  self.BTN_W, self.BTN_H, T("menu_quit"),     self.font_btn),
        }

    @staticmethod
    def _new_p():
        return {"x": random.uniform(0, SCREEN_W), "y": random.uniform(0, SCREEN_H),
                "vy": random.uniform(-0.3, -0.8),  "vx": random.uniform(-0.2, 0.2),
                "size": random.uniform(1, 3),       "alpha": random.randint(30, 120),
                "color": random.choice([(120,80,255),(80,160,255),(255,100,180),(100,220,255)])}

    def _update_bg(self):
        for i, p in enumerate(self._bg_parts):
            p["x"] += p["vx"]; p["y"] += p["vy"]
            if p["y"] < -5 or not (0 <= p["x"] <= SCREEN_W):
                np = self._new_p(); np["y"] = SCREEN_H + 5
                self._bg_parts[i] = np

    def _draw_bg(self, surf):
        for p in self._bg_parts:
            s = pygame.Surface((int(p["size"]*2+2),)*2, pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["color"], p["alpha"]),
                               (int(p["size"]+1),)*2, int(p["size"]))
            surf.blit(s, (int(p["x"]), int(p["y"])))

    def handle_events(self, events) -> Optional[str]:
        mx, my = pygame.mouse.get_pos()
        for btn in self.buttons.values():
            btn.update(mx, my)
        for ev in events:
            for bid, btn in self.buttons.items():
                if btn.is_clicked(ev):
                    return bid
        return None

    def draw(self, surf):
        self.tick += 1
        # Arka plan
        surf.fill((8, 6, 16))
        for y in range(0, SCREEN_H, 4):
            t = y / SCREEN_H
            pygame.draw.line(surf, (int(8+12*(1-t)), int(6+8*(1-t)), int(16+28*(1-t))),
                             (0, y), (SCREEN_W, y))
        self._update_bg(); self._draw_bg(surf)
        # Başlık
        float_y  = math.sin(self.tick * 0.03) * 6
        pulse    = 0.5 + 0.5 * math.sin(self.tick * 0.05)
        tclr     = (int(160+95*pulse), int(80+60*pulse), 255)
        ts       = self.font_title.render(T("title"), True, tclr)
        sh       = self.font_title.render(T("title"), True, (20,10,40))
        ty       = int(SCREEN_H * 0.13 + float_y)
        surf.blit(sh, (SCREEN_W//2 - ts.get_width()//2 + 3, ty + 4))
        surf.blit(ts, (SCREEN_W//2 - ts.get_width()//2,     ty))
        sub = self.font_sub.render("Vampire Survivors Clone", True, (120,110,160))
        surf.blit(sub, sub.get_rect(centerx=SCREEN_W//2, y=ty + ts.get_height() + 4))
        line_y = ty + ts.get_height() + 32
        pygame.draw.line(surf, (80,60,140), (SCREEN_W//2-160, line_y), (SCREEN_W//2+160, line_y), 1)
        for btn in self.buttons.values():
            btn.draw(surf)
        ver = self.font_ver.render("v2.0 - Boss Altın Karakter Sandık Drone Taret",
                                   True, (60,55,90))
        surf.blit(ver, (12, SCREEN_H - 20))
        pygame.display.flip()

    def refresh_labels(self):
        self.buttons["play"].label     = T("menu_play")
        self.buttons["campaign"].label = T("menu_campaign")
        self.buttons["chars"].label    = T("menu_chars")
        self.buttons["settings"].label = T("menu_settings")
        self.buttons["quit"].label     = T("menu_quit")


# ---------------------------------------------------------------------------
# Campaign Ekranı
# ---------------------------------------------------------------------------
class CampaignScreen:
    COLS = 5
    ROWS = 6
    BTN_W, BTN_H = 150, 56
    GAP_X, GAP_Y = 22, 18

    def __init__(self, save: SaveData):
        self.save = save
        self.tick = 0
        self.font_title = pygame.font.SysFont("segoeui", 44, bold=True)
        self.font_btn   = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_sm    = pygame.font.SysFont("segoeui", 14, bold=True)
        self.font_back  = pygame.font.SysFont("segoeui", 20, bold=True)
        self._build_buttons()

    def _build_buttons(self):
        total_w = self.COLS * self.BTN_W + (self.COLS - 1) * self.GAP_X
        sx = SCREEN_W // 2 - total_w // 2
        sy = 150
        self.level_buttons = []
        for i in range(30):
            col = i % self.COLS
            row = i // self.COLS
            x = sx + col * (self.BTN_W + self.GAP_X)
            y = sy + row * (self.BTN_H + self.GAP_Y)
            self.level_buttons.append(
                Button(x, y, self.BTN_W, self.BTN_H,
                       T("campaign_level", n=i + 1), self.font_btn)
            )
        self.btn_back = Button(SCREEN_W // 2 - 100, SCREEN_H - 70,
                               200, 46, T("menu_back"), self.font_back)

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        for btn in self.level_buttons:
            btn.update(mx, my)
        self.btn_back.update(mx, my)

        for ev in events:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return "back"
            if self.btn_back.is_clicked(ev):
                return "back"
            for i, btn in enumerate(self.level_buttons):
                level = i + 1
                if level <= self.save.campaign_unlocked_level and btn.is_clicked(ev):
                    return level
        return None

    def draw(self, surf):
        self.tick += 1
        surf.fill((8, 6, 16))
        for y in range(0, SCREEN_H, 4):
            t = y / SCREEN_H
            pygame.draw.line(surf, (int(8+12*(1-t)), int(6+8*(1-t)), int(16+28*(1-t))),
                             (0, y), (SCREEN_W, y))

        title = self.font_title.render(T("campaign_title"), True, (180,140,255))
        surf.blit(title, title.get_rect(centerx=SCREEN_W//2, y=42))
        pygame.draw.line(surf, (80,60,140), (SCREEN_W//2-220, 104), (SCREEN_W//2+220, 104), 1)

        for i, btn in enumerate(self.level_buttons):
            level = i + 1
            unlocked = level <= self.save.campaign_unlocked_level
            completed = level < self.save.campaign_unlocked_level
            btn.label = T("campaign_level", n=level)
            btn.draw(surf)
            rect = btn.base_rect

            target = self.font_sm.render(
                T("target_wave", n=campaign_target_wave(level)),
                True, (155,150,195) if unlocked else (95,90,120))
            surf.blit(target, target.get_rect(centerx=rect.centerx, y=rect.y + 34))

            if completed:
                mark = self.font_sm.render(T("completed"), True, C_GREEN)
                surf.blit(mark, mark.get_rect(centerx=rect.centerx, y=rect.y - 16))
            elif not unlocked:
                locked = self.font_sm.render(T("locked"), True, C_RED)
                cover = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                cover.fill((0, 0, 0, 115))
                surf.blit(cover, rect.topleft)
                surf.blit(locked, locked.get_rect(center=rect.center))

        self.btn_back.draw(surf)
        pygame.display.flip()

    def refresh_labels(self):
        self.btn_back.label = T("menu_back")
        for i, btn in enumerate(self.level_buttons):
            btn.label = T("campaign_level", n=i + 1)


# ---------------------------------------------------------------------------
# Ayarlar Ekranı
# ---------------------------------------------------------------------------
class SettingsScreen:
    def __init__(self, sfx):
        self.sfx        = sfx
        self.fullscreen = False
        self.tick       = 0
        self.font_title = pygame.font.SysFont("segoeui", 44, bold=True)
        self.font_lbl   = pygame.font.SysFont("segoeui", 22)
        self.font_btn   = pygame.font.SysFont("segoeui", 20, bold=True)
        self._build_buttons()

    def _build_buttons(self):
        cx   = SCREEN_W // 2
        ry   = SCREEN_H // 2 - 55
        step = 70
        self.btn_sound = Button(cx - 60, ry,        120, 48, self._slbl(), self.font_btn)
        self.btn_fs    = Button(cx - 60, ry + step,  120, 48, self._flbl(), self.font_btn)
        self.btn_back  = Button(cx - 100, ry + step*2+10, 200, 48, T("menu_back"), self.font_btn)

    def _slbl(self): return T("menu_sound_off") if self.sfx.muted else T("menu_sound_on")
    def _flbl(self): return T("menu_fs_on") if self.fullscreen else T("menu_fs_off")

    def handle_events(self, events) -> Optional[str]:
        mx, my = pygame.mouse.get_pos()
        for btn in (self.btn_sound, self.btn_fs, self.btn_back):
            btn.update(mx, my)
        for ev in events:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return "back"
            if self.btn_sound.is_clicked(ev):
                self.sfx.toggle_mute(); self.btn_sound.label = self._slbl()
            elif self.btn_fs.is_clicked(ev):
                self.fullscreen = not self.fullscreen
                flags = pygame.FULLSCREEN if self.fullscreen else 0
                pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
                self.btn_fs.label = self._flbl()
            elif self.btn_back.is_clicked(ev):
                return "back"
        return None

    def draw(self, surf):
        self.tick += 1
        surf.fill((10, 8, 20))
        for y in range(0, SCREEN_H, 4):
            t = y / SCREEN_H
            pygame.draw.line(surf, (int(10+10*(1-t)), int(8+6*(1-t)), int(20+24*(1-t))),
                             (0, y), (SCREEN_W, y))
        title = self.font_title.render(T("menu_settings"), True, (180,140,255))
        surf.blit(title, title.get_rect(centerx=SCREEN_W//2, y=80))
        pygame.draw.line(surf, (80,60,140), (SCREEN_W//2-200, 140), (SCREEN_W//2+200, 140), 1)
        ry   = SCREEN_H // 2 - 55
        step = 70
        lbls = [T("menu_sound"), T("menu_fullscreen")]
        for i, lbl in enumerate(lbls):
            s = self.font_lbl.render(lbl, True, (180,175,220))
            surf.blit(s, (SCREEN_W//2 - 200, ry + i * step + 12))
        self.btn_sound.draw(surf)
        self.btn_fs.draw(surf)
        self.btn_back.draw(surf)
        pygame.display.flip()

    def refresh_labels(self):
        self.btn_sound.label = self._slbl()
        self.btn_fs.label    = self._flbl()
        self.btn_back.label  = T("menu_back")


# ---------------------------------------------------------------------------
# Karakter Seçim Ekranı
# ---------------------------------------------------------------------------
class CharacterScreen:
    """
    Karakterleri kart olarak gösterir.
    Kilitli olanlar altın ile açılabilir.
    Açık olanlar seçilebilir.
    """
    CARD_W, CARD_H = 240, 200
    GAP            = 30

    def __init__(self, save: SaveData):
        self.save      = save
        self.tick      = 0
        self.notice    = ""       # "Yetersiz Altın" gibi kısa bildirimler
        self.notice_cd = 0
        self.font_title = pygame.font.SysFont("segoeui", 40, bold=True)
        self.font_name  = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_desc  = pygame.font.SysFont("segoeui", 16)
        self.font_cost  = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_back  = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_gold  = pygame.font.SysFont("segoeui", 20, bold=True)
        bx = SCREEN_W // 2 - 100
        self.btn_back = Button(bx, SCREEN_H - 70, 200, 46, T("menu_back"), self.font_back)

    def _card_rects(self):
        total_w = len(CHARACTER_DEFS) * self.CARD_W + (len(CHARACTER_DEFS)-1) * self.GAP
        sx      = SCREEN_W // 2 - total_w // 2
        cy      = SCREEN_H // 2 - self.CARD_H // 2 + 10
        return [pygame.Rect(sx + i*(self.CARD_W + self.GAP), cy, self.CARD_W, self.CARD_H)
                for i in range(len(CHARACTER_DEFS))]

    def handle_events(self, events) -> Optional[str]:
        mx, my = pygame.mouse.get_pos()
        self.btn_back.update(mx, my)
        rects = self._card_rects()
        if self.notice_cd > 0:
            self.notice_cd -= 1
        for ev in events:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return "back"
            if self.btn_back.is_clicked(ev):
                return "back"
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(ev.pos):
                        cdef = CHARACTER_DEFS[i]
                        if cdef["id"] in self.save.unlocked_ids:
                            self.save.selected_id = cdef["id"]
                        elif self.save.total_gold >= cdef["cost"]:
                            self.save.unlock(cdef["id"], cdef["cost"])
                            self.save.selected_id = cdef["id"]
                        else:
                            self.notice    = T("not_enough")
                            self.notice_cd = 120
        return None

    def draw(self, surf):
        self.tick += 1
        surf.fill((8, 6, 16))
        for y in range(0, SCREEN_H, 4):
            t = y / SCREEN_H
            pygame.draw.line(surf, (int(8+12*(1-t)), int(6+8*(1-t)), int(16+28*(1-t))),
                             (0, y), (SCREEN_W, y))
        # Başlık
        title = self.font_title.render(T("menu_chars"), True, (180,140,255))
        surf.blit(title, title.get_rect(centerx=SCREEN_W//2, y=28))
        # Altın gösterge
        gold_s = self.font_gold.render(f"{T('gold')}: {self.save.total_gold}", True, C_YELLOW)
        surf.blit(gold_s, (SCREEN_W - gold_s.get_width() - 20, 30))

        rects = self._card_rects()
        mx, my = pygame.mouse.get_pos()

        for i, (cdef, rect) in enumerate(zip(CHARACTER_DEFS, rects)):
            cid      = cdef["id"]
            owned    = cid in self.save.unlocked_ids
            selected = cid == self.save.selected_id
            hovering = rect.collidepoint(mx, my)

            # Kart arka plan
            bg_alpha = 220 if hovering else 160
            card_s   = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            card_s.fill((*C_UI_BG[:3], bg_alpha))
            surf.blit(card_s, rect.topleft)

            border_c = cdef["color"] if selected else ((180,180,255) if hovering else (60,60,100))
            border_w = 3 if selected else (2 if hovering else 1)
            pygame.draw.rect(surf, border_c, rect, border_w, border_radius=8)

            # Karakter renk dairesi
            pygame.draw.circle(surf, cdef["color"],
                               (rect.centerx, rect.y + 52), 28)
            pygame.draw.circle(surf, C_WHITE,
                               (rect.centerx, rect.y + 52), 28, 2)

            # İsim
            char_name = STRINGS[LANG]["char_names"][cid]
            ns = self.font_name.render(char_name, True,
                                       cdef["color"] if owned else (120,120,120))
            surf.blit(ns, ns.get_rect(centerx=rect.centerx, y=rect.y + 90))

            # Açıklama
            char_desc = STRINGS[LANG]["char_descs"][cid]
            ds = self.font_desc.render(char_desc, True, (180,180,220))
            surf.blit(ds, ds.get_rect(centerx=rect.centerx, y=rect.y + 118))

            # Alt buton: Satın Al / SAHİP / SEÇİLDİ
            if selected:
                lbl_s = self.font_cost.render(T("selected"), True, C_GREEN)
            elif owned:
                lbl_s = self.font_cost.render(T("owned"), True, (140,220,140))
            else:
                cost_s = self.font_cost.render(
                    f"{cdef['cost']}  {T('buy')}", True,
                    C_YELLOW if self.save.total_gold >= cdef["cost"] else C_RED)
                lbl_s  = cost_s
            surf.blit(lbl_s, lbl_s.get_rect(centerx=rect.centerx, y=rect.y + 158))

            # Kilit simgesi (sahip değilse)
            if not owned:
                lock_s = self.font_desc.render(T("locked"), True, (160,100,100))
                surf.blit(lock_s, lock_s.get_rect(centerx=rect.centerx, y=rect.y + 10))

        self.btn_back.draw(surf)

        # Bildirim
        if self.notice_cd > 0:
            alpha  = min(255, self.notice_cd * 4)
            ns     = self.font_cost.render(self.notice, True, C_RED)
            ns.set_alpha(alpha)
            surf.blit(ns, ns.get_rect(centerx=SCREEN_W//2, y=SCREEN_H - 110))

        pygame.display.flip()


# ---------------------------------------------------------------------------
# Ana oyun
# ---------------------------------------------------------------------------
# Boss spawn aralığı (saniye)
BOSS_INTERVAL = 120   # 2 dakikada bir boss

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Vampire Survivors Clone")
        self.clock  = pygame.time.Clock()
        self.sfx    = SoundEngine()

        self.font_sm   = pygame.font.SysFont("segoeui", 16)
        self.font_med  = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_big  = pygame.font.SysFont("segoeui", 36, bold=True)
        self.font_dmg  = pygame.font.SysFont("segoeui", 15, bold=True)

        # Kalıcı veriler (menüler arası korunur)
        self.save          = SaveData()

        # State machine
        self.state         = GameState.MENU
        self.main_menu     = MainMenu(self.sfx)
        self.campaign_scr  = CampaignScreen(self.save)
        self.settings_scr  = SettingsScreen(self.sfx)
        self.char_scr      = CharacterScreen(self.save)
        self.campaign_mode = False
        self.campaign_level = 1
        self.level_completed = False
        btn_y = SCREEN_H // 2 + 90
        self.btn_next_level = Button(SCREEN_W // 2 - 240, btn_y, 220, 52,
                                     T("next_level"), self.font_med)
        self.btn_completed_menu = Button(SCREEN_W // 2 + 20, btn_y, 220, 52,
                                         T("main_menu"), self.font_med)

        self.reset()

    # -----------------------------------------------------------------------
    def _apply_char_mods(self):
        """Seçili karakterin başlangıç modifierlerini oyuncuya uygula."""
        p    = self.player
        cdef = next(c for c in CHARACTER_DEFS if c["id"] == self.save.selected_id)
        mods = cdef["mods"]
        if "max_hp"     in mods: p.max_hp   += mods["max_hp"];   p.hp += mods["max_hp"]
        if "armor"      in mods: p.armor    += mods["armor"]
        if "speed_mult" in mods: p.speed_mult += mods["speed_mult"]
        if "recovery"   in mods: p.recovery += mods["recovery"]
        if "orb_level"  in mods:
            for _ in range(mods["orb_level"]):
                p.orb.upgrade()

    # -----------------------------------------------------------------------
    def reset(self):
        cdef = next(c for c in CHARACTER_DEFS if c["id"] == self.save.selected_id)
        self.player       = Player(WORLD_W // 2, WORLD_H // 2,
                                   character_id=cdef["id"], color=cdef["color"])
        self.player.lightning_staff = LightningStaffWeapon()
        self.player.ice_wand = IceWandWeapon()
        self._apply_char_mods()

        self.enemies:       List[Enemy]       = []
        self.bosses:        List[Boss]        = []    # boss listesi
        self.enemy_projs:   List[Projectile]  = []
        self.player_projs:  List[Projectile]  = []   # drone/taret mermileri
        self.particles:     List[Particle]    = []
        self.damage_numbers:List[DamageNumber]= []
        self.xp_gems:       List[XPGem]       = []
        self.gold_coins:    List[GoldCoin]    = []   # altın

        # Sandıklar — 5 adet başlangıçta
        self.chests: List[Chest]  = [Chest() for _ in range(5)]
        # Dronelar ve taretler
        self.drones:  List[Drone]  = []
        self.turrets: List[Turret] = []

        self.spawn_mgr   = SpawnManager()
        self.tick        = 0
        self.paused      = False
        self.game_over   = False
        self.level_completed = False
        self.upgrade_screen: Optional[UpgradeScreen] = None
        self.kills       = 0
        self.session_gold = 0         # bu oyunda kazanılan altın

        # Boss bildirim
        self.boss_alert_timer = 0     # ekranda "BOSS FIGHT!" yazısı kalma süresi

        self.cam_x = self.player.x - SCREEN_W // 2
        self.cam_y = self.player.y - SCREEN_H // 2

    # -----------------------------------------------------------------------
    # State geçişleri
    # -----------------------------------------------------------------------
    def _go_menu(self):
        # Oyun bittiyse kazanılan altını kaydet
        self.save.total_gold += self.session_gold
        self.session_gold     = 0
        self.campaign_mode = False
        self.state = GameState.MENU
        self.main_menu.refresh_labels()
        self.campaign_scr = CampaignScreen(self.save)
        self.char_scr = CharacterScreen(self.save)   # altın güncellendi

    def _go_settings(self):
        self.state = GameState.SETTINGS
        self.settings_scr.refresh_labels()

    def _go_campaign(self):
        self.state = GameState.CAMPAIGN
        self.campaign_scr.refresh_labels()

    def _go_chars(self):
        self.state    = GameState.CHARACTERS
        self.char_scr = CharacterScreen(self.save)

    def _go_playing(self, campaign_level=None):
        self.campaign_mode = campaign_level is not None
        if campaign_level is not None:
            self.campaign_level = campaign_level
        self.reset()
        self.state = GameState.PLAYING

    def _complete_campaign_level(self):
        self.level_completed = True
        self.paused = True
        self.upgrade_screen = None
        self.save.total_gold += self.session_gold
        self.session_gold = 0
        self.save.complete_campaign_level(self.campaign_level)
        self.campaign_scr = CampaignScreen(self.save)

    def _go_next_campaign_level(self):
        next_level = min(30, self.campaign_level + 1)
        if next_level <= self.save.campaign_unlocked_level:
            self._go_playing(next_level)
        else:
            self._go_menu()

    # -----------------------------------------------------------------------
    def run(self):
        while True:
            self.clock.tick(FPS)
            raw = pygame.event.get()

            for ev in raw:
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

            # ── MENU ───────────────────────────────────────────────────────
            if self.state == GameState.MENU:
                action = self.main_menu.handle_events(raw)
                if   action == "play":     self._go_playing()
                elif action == "campaign": self._go_campaign()
                elif action == "chars":    self._go_chars()
                elif action == "settings": self._go_settings()
                elif action == "quit":     pygame.quit(); sys.exit()
                else:
                    for ev in raw:
                        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_l:
                            toggle_lang(); self.main_menu.refresh_labels()
                    self.main_menu.draw(self.screen)

            # ── CAMPAIGN ──────────────────────────────────────────────────
            elif self.state == GameState.CAMPAIGN:
                action = self.campaign_scr.handle_events(raw)
                if action == "back":
                    self._go_menu()
                elif isinstance(action, int):
                    self._go_playing(action)
                else:
                    for ev in raw:
                        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_l:
                            toggle_lang(); self.campaign_scr.refresh_labels()
                    self.campaign_scr.draw(self.screen)

            # ── SETTINGS ───────────────────────────────────────────────────
            elif self.state == GameState.SETTINGS:
                action = self.settings_scr.handle_events(raw)
                if action == "back": self._go_menu()
                else: self.settings_scr.draw(self.screen)

            # ── CHARACTERS ─────────────────────────────────────────────────
            elif self.state == GameState.CHARACTERS:
                action = self.char_scr.handle_events(raw)
                if action == "back": self._go_menu()
                else: self.char_scr.draw(self.screen)

            # ── PLAYING ────────────────────────────────────────────────────
            elif self.state == GameState.PLAYING:
                for ev in raw:
                    if self.level_completed:
                        mx, my = pygame.mouse.get_pos()
                        self.btn_next_level.update(mx, my)
                        self.btn_completed_menu.update(mx, my)
                        if self.btn_next_level.is_clicked(ev):
                            if self.campaign_level < 30:
                                self._go_next_campaign_level()
                            else:
                                self._go_menu()
                            break
                        if self.btn_completed_menu.is_clicked(ev):
                            self._go_menu(); break
                        continue
                    if ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_ESCAPE:
                            self._go_menu(); break
                        if ev.key == pygame.K_p:
                            self.paused = not self.paused
                        if ev.key == pygame.K_l:
                            toggle_lang()
                        if ev.key == pygame.K_m:
                            self.sfx.toggle_mute()
                        if self.game_over and ev.key == pygame.K_r:
                            self._go_playing(self.campaign_level if self.campaign_mode else None); break
                    if self.upgrade_screen:
                        result = self.upgrade_screen.handle_event(ev)
                        if result:
                            self._apply_upgrade(result)
                            self.upgrade_screen = None
                            self.paused = False

                if self.state == GameState.PLAYING:
                    if not self.paused and not self.game_over and not self.upgrade_screen and not self.level_completed:
                        self._update()
                    self._draw()

    # -----------------------------------------------------------------------
    def _apply_upgrade(self, ut: UpgradeType):
        p = self.player
        if ut == UpgradeType.MAX_HP:   p.max_hp += 40; p.hp = min(p.max_hp, p.hp + 40)
        elif ut == UpgradeType.SPEED:  p.speed_mult *= 1.10
        elif ut == UpgradeType.WHIP:   p.whip.upgrade()
        elif ut == UpgradeType.ORB:    p.orb.upgrade()
        elif ut == UpgradeType.AURA:      p.aura.upgrade()
        elif ut == UpgradeType.BOOMERANG: p.boomerang.upgrade()
        elif ut == UpgradeType.LIGHTNING_STAFF: p.lightning_staff.upgrade()
        elif ut == UpgradeType.ICE_WAND: p.ice_wand.upgrade()
        elif ut == UpgradeType.RECOVERY:  p.recovery += 1
        elif ut == UpgradeType.ARMOR:  p.armor += 2

    # -----------------------------------------------------------------------
    def _update(self):
        self.tick += 1
        keys = pygame.key.get_pressed()
        p    = self.player

        p.update(keys, 1 / FPS)

        # Kamera
        target_cx = p.x - SCREEN_W // 2
        target_cy = p.y - SCREEN_H // 2
        self.cam_x = lerp(self.cam_x, target_cx, 0.12)
        self.cam_y = lerp(self.cam_y, target_cy, 0.12)

        # Normal spawn
        self.spawn_mgr.update(p, self.enemies, self.tick)

        if (self.campaign_mode and not self.level_completed
                and self.spawn_mgr.wave + 1 >= campaign_target_wave(self.campaign_level)):
            self._complete_campaign_level()
            return

        # ── Boss spawn ──────────────────────────────────────────────────
        if self.tick > 0 and self.tick % (BOSS_INTERVAL * FPS) == 0:
            # Ekranın dışında spawn et
            side = random.randint(0, 3)
            if side == 0:   bx, by = p.x + random.uniform(-400,400), p.y - 500
            elif side == 1: bx, by = p.x + 600, p.y + random.uniform(-400,400)
            elif side == 2: bx, by = p.x + random.uniform(-400,400), p.y + 500
            else:           bx, by = p.x - 600, p.y + random.uniform(-400,400)
            bx = clamp(bx, 100, WORLD_W-100)
            by = clamp(by, 100, WORLD_H-100)
            self.bosses.append(Boss(bx, by, self.spawn_mgr.wave))
            self.boss_alert_timer = 240   # 4 sn bildiri

        if self.boss_alert_timer > 0:
            self.boss_alert_timer -= 1

        # Silahlar
        p.whip.update(p, self.enemies + self.bosses, self.particles, self.damage_numbers, self.sfx)
        p.orb.update(p,  self.enemies + self.bosses, self.particles, self.damage_numbers, self.sfx)
        p.aura.update(p, self.enemies + self.bosses, self.particles, self.damage_numbers, self.sfx)
        p.boomerang.update(p, self.enemies + self.bosses, self.particles, self.damage_numbers, self.sfx)
        p.lightning_staff.update(p, self.enemies + self.bosses, self.particles, self.damage_numbers, self.sfx)
        p.ice_wand.update(p, self.enemies + self.bosses, self.particles, self.damage_numbers, self.sfx)

        # ── Drone güncelle ──────────────────────────────────────────────
        all_enemies = self.enemies + self.bosses
        for drone in self.drones:
            drone.update(p, all_enemies, self.player_projs, self.damage_numbers, self.particles)

        # ── Taret güncelle ─────────────────────────────────────────────
        for turret in self.turrets:
            turret.update(all_enemies, self.player_projs, self.damage_numbers, self.particles)
        self.turrets = [t for t in self.turrets if t.alive]

        # ── Player mermileri (drone/taret) düşmanlara çarpma ───────────
        for proj in self.player_projs:
            proj.update()
            if proj.alive:
                for e in all_enemies:
                    if e.alive and id(e) not in proj.hit_set:
                        if dist((proj.x, proj.y), (e.x, e.y)) < proj.size + e.radius:
                            e.take_damage(proj.damage)
                            proj.hit_set.add(id(e))
                            proj.pierce -= 1
                            self.damage_numbers.append(
                                DamageNumber(e.x, e.y, proj.damage, proj.color))
                            for _ in range(4):
                                self.particles.append(
                                    Particle(proj.x, proj.y, proj.color, speed=2))
                            if proj.pierce <= 0:
                                proj.alive = False
                                break

        # Normal düşman güncellemeleri
        new_ep = []
        for e in self.enemies:
            e.update(p, new_ep)
        self.enemy_projs.extend(new_ep)

        # Boss güncellemeleri
        boss_ep = []
        for b in self.bosses:
            b.update(p, boss_ep)
        self.enemy_projs.extend(boss_ep)

        # Düşman mermileri
        for proj in self.enemy_projs:
            proj.update()
            if proj.alive:
                if dist((proj.x, proj.y), (p.x, p.y)) < p.radius + proj.size:
                    p.take_damage(proj.damage)
                    self.sfx.play_damage()
                    for _ in range(4):
                        self.particles.append(Particle(proj.x, proj.y, C_RED, speed=3))
                    proj.alive = False

        # Melee çarpışma (normal düşman + boss)
        for e in self.enemies:
            if e.alive and dist((e.x, e.y), (p.x, p.y)) < e.radius + p.radius:
                p.take_damage(e.damage); self.sfx.play_damage()
        for b in self.bosses:
            if b.alive and dist((b.x, b.y), (p.x, p.y)) < b.radius + p.radius:
                p.take_damage(b.damage); self.sfx.play_damage()

        # XP gem toplama
        collected = 0
        for gem in self.xp_gems:
            collected += gem.update(p)
        if collected:
            self.sfx.play_xp()
            if p.gain_xp(collected):
                self.sfx.play_levelup(); self._trigger_levelup()

        # ── Altın toplama ───────────────────────────────────────────────
        for coin in self.gold_coins:
            v = coin.update(p)
            if v:
                self.session_gold += v

        # ── Sandık etkileşimi ───────────────────────────────────────────
        for chest in self.chests:
            drop = chest.update(p)
            if drop == ChestDrop.GOLD:
                amt = random.randint(20, 50)
                self.session_gold += amt
                self.damage_numbers.append(
                    DamageNumber(p.x, p.y - 30, f"+{amt}G", C_YELLOW))
            elif drop == ChestDrop.DRONE:
                self.drones.append(Drone(index=len(self.drones)))
                self.damage_numbers.append(
                    DamageNumber(p.x, p.y - 30, "+Drone", C_CYAN))
            elif drop == ChestDrop.TURRET:
                self.turrets.append(Turret(p.x, p.y))
                self.damage_numbers.append(
                    DamageNumber(p.x, p.y - 30, "+Taret", (255,180,40)))

        # Ölen normal düşmanlar
        dead = [e for e in self.enemies if not e.alive]
        for e in dead:
            self.kills += 1
            self.sfx.play_death()
            self.xp_gems.append(XPGem(e.x, e.y, e.xp))
            # %40 altın düşürür
            if random.random() < 0.40:
                val = random.randint(1, 5)
                self.gold_coins.append(GoldCoin(e.x, e.y, val))
            for _ in range(8):
                self.particles.append(Particle(e.x, e.y, e.color, speed=3, life=40))

        # ── Ölen bosslar ───────────────────────────────────────────────
        dead_bosses = [b for b in self.bosses if not b.alive]
        for b in dead_bosses:
            self.kills += 1
            self.sfx.play_death()
            # Yüksek XP
            self.xp_gems.append(XPGem(b.x, b.y, b.XP_REWARD))
            # Yüksek altın
            for _ in range(8):
                val = random.randint(8, 18)
                self.gold_coins.append(GoldCoin(
                    b.x + random.uniform(-40, 40),
                    b.y + random.uniform(-40, 40), val))
            for _ in range(30):
                self.particles.append(Particle(b.x, b.y, Boss.COLOR, speed=5, life=60))
            for _ in range(15):
                self.particles.append(Particle(b.x, b.y, C_YELLOW, speed=4, life=50))

        # Temizlik
        self.enemies        = [e for e in self.enemies if e.alive]
        self.bosses         = [b for b in self.bosses  if b.alive]
        self.enemy_projs    = [p2 for p2 in self.enemy_projs   if p2.alive]
        self.player_projs   = [p2 for p2 in self.player_projs  if p2.alive]
        self.particles      = [pt for pt in self.particles      if pt.update()]
        self.damage_numbers = [d  for d  in self.damage_numbers if d.update()]
        self.xp_gems        = [g  for g  in self.xp_gems        if g.alive]
        self.gold_coins     = [c  for c  in self.gold_coins     if c.alive]

        # Game over
        if p.hp <= 0:
            p.hp = 0
            self.game_over = True
            # Altını kaydet (game over ekranında göstermek için)
            self.save.total_gold += self.session_gold
            self.session_gold     = 0

    def _trigger_levelup(self):
        self.paused = True
        self.upgrade_screen = UpgradeScreen(list(UpgradeType))

    # -----------------------------------------------------------------------
    def _draw(self):
        surf = self.screen
        surf.fill(C_BG)
        cx, cy = int(self.cam_x), int(self.cam_y)

        # Grid
        start_tx = (cx // TILE) * TILE
        start_ty = (cy // TILE) * TILE
        for gx in range(start_tx, cx + SCREEN_W + TILE, TILE):
            pygame.draw.line(surf, C_GRID, (gx - cx, 0), (gx - cx, SCREEN_H))
        for gy in range(start_ty, cy + SCREEN_H + TILE, TILE):
            pygame.draw.line(surf, C_GRID, (0, gy - cy), (SCREEN_W, gy - cy))

        # Taretler (zemin seviyesinde, düşmanların altında)
        for t in self.turrets:
            t.draw(surf, cx, cy)

        # Sandıklar
        for chest in self.chests:
            chest.draw(surf, cx, cy)

        # XP gem + altın
        for gem in self.xp_gems:
            gem.draw(surf, cx, cy, self.tick)
        for coin in self.gold_coins:
            coin.draw(surf, cx, cy)

        # Aura / Orb / Whip / Boomerang
        self.player.aura.draw(surf, cx, cy, self.player, self.tick)
        self.player.orb.draw(surf,  cx, cy, self.player, self.tick)
        self.player.whip.draw(surf, cx, cy, self.player)
        self.player.boomerang.draw(surf, cx, cy, self.player)
        self.player.lightning_staff.draw(surf, cx, cy, self.tick)
        self.player.ice_wand.draw(surf, cx, cy, self.tick)

        # Dronelar
        for drone in self.drones:
            drone.draw(surf, cx, cy, self.player)

        # Düşmanlar
        for e in self.enemies:
            e.draw(surf, cx, cy)

        # Bosslar
        for b in self.bosses:
            b.draw(surf, cx, cy)

        # Mermiler (düşman + player)
        for proj in self.enemy_projs:
            proj.draw(surf, cx, cy)
        for proj in self.player_projs:
            proj.draw(surf, cx, cy)

        # Particles + hasar sayıları
        for pt in self.particles:
            pt.draw(surf, cx, cy)
        for dn in self.damage_numbers:
            dn.draw(surf, cx, cy, self.font_dmg)

        # Oyuncu
        self.player.draw(surf, cx, cy, self.tick)

        # UI
        self._draw_ui(surf)

        # Boss bildirimi
        if self.boss_alert_timer > 0:
            self._draw_boss_alert(surf)

        if self.upgrade_screen:
            self.upgrade_screen.draw(surf)
        if self.level_completed:
            self._draw_level_completed(surf)
        elif self.paused and not self.upgrade_screen:
            self._draw_pause(surf)
        if self.game_over:
            self._draw_game_over(surf)

        pygame.display.flip()

    # -----------------------------------------------------------------------
    def _draw_ui(self, surf):
        p = self.player

        # HP çubuğu
        bar_w = 220
        bx, by = 16, 16
        pygame.draw.rect(surf, C_HP_BG, (bx, by, bar_w, 18), border_radius=4)
        fill = int(bar_w * p.hp / p.max_hp)
        pygame.draw.rect(surf, C_HP, (bx, by, fill, 18), border_radius=4)
        pygame.draw.rect(surf, (200,200,200), (bx, by, bar_w, 18), 1, border_radius=4)
        surf.blit(self.font_sm.render(f"{T('hp')}  {p.hp}/{p.max_hp}", True, C_WHITE),
                  (bx + 4, by + 2))

        # XP çubuğu
        bx2, by2 = 16, 42
        pygame.draw.rect(surf, C_XP_BG, (bx2, by2, bar_w, 12), border_radius=4)
        fill2 = int(bar_w * p.xp / p.xp_needed)
        pygame.draw.rect(surf, C_XP, (bx2, by2, fill2, 12), border_radius=4)
        pygame.draw.rect(surf, (200,200,200), (bx2, by2, bar_w, 12), 1, border_radius=4)
        surf.blit(self.font_sm.render(
            f"{T('lv')} {p.level}  {T('xp')} {p.xp}/{p.xp_needed}", True, C_WHITE),
            (bx2 + 4, by2 - 1))

        # Süre, dalga, kill (üst orta)
        elapsed = self.tick // FPS
        mins, secs = divmod(elapsed, 60)
        wave = self.spawn_mgr.wave
        info = self.font_med.render(
            f"{mins:02d}:{secs:02d}   {T('wave')} {wave+1}   {T('kill')} {self.kills}",
            True, C_YELLOW)
        surf.blit(info, (SCREEN_W//2 - info.get_width()//2, 12))

        self._draw_weapons_panel(surf)

        # Sağ üst: ses + dil
        mute_label = T("muted") if self.sfx.muted else T("unmuted")
        mute_col   = (200,80,80) if self.sfx.muted else (80,200,80)
        ml = self.font_sm.render(f"{mute_label}  |  {T('lang_label')}", True, mute_col)
        surf.blit(ml, (SCREEN_W - ml.get_width() - 12, 16))

        # Altın (sağ üst, ikinci satır)
        gold_s = self.font_sm.render(
            f"{T('gold')}: {self.save.total_gold + self.session_gold}", True, C_YELLOW)
        surf.blit(gold_s, (SCREEN_W - gold_s.get_width() - 12, 36))

        if self.campaign_mode:
            c_s = self.font_sm.render(
                f"{T('campaign_level', n=self.campaign_level)}  |  "
                f"{T('target_wave', n=campaign_target_wave(self.campaign_level))}",
                True, (180, 175, 230))
            surf.blit(c_s, (SCREEN_W - c_s.get_width() - 12, 56))

        # Drone / Taret sayısı
        if self.drones or self.turrets:
            dt_s = self.font_sm.render(
                f"Drone: {len(self.drones)}  Taret: {len(self.turrets)}",
                True, (180,220,255))
            surf.blit(dt_s, (16, SCREEN_H - 44))

        # Kontrol ipuçları (alt orta)
        hint = self.font_sm.render(T("controls"), True, (100,100,140))
        surf.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 24))

    # -----------------------------------------------------------------------
    def _draw_weapons_panel(self, surf):
        p = self.player

        if not hasattr(self, "_wpn_font_title"):
            self._wpn_font_title = pygame.font.SysFont("segoeui", 14, bold=True)
            self._wpn_font_row   = pygame.font.SysFont("segoeui", 13)

        rows = [
            (T("wpn_whip"),      f"Lv{p.whip.level}"),
            (T("wpn_orb"),       f"Lv{p.orb.level}"),
            (T("wpn_aura"),      f"Lv{p.aura.level}"),
            (T("wpn_boomerang"), f"Lv{p.boomerang.level}"),
            (T("wpn_lightning"), f"Lv{p.lightning_staff.level}"),
            (T("wpn_ice"),       f"Lv{p.ice_wand.level}"),
            (T("wpn_armor"),     f"{p.armor}"),
            (T("wpn_regen"),     f"{p.recovery}"),
        ]

        PANEL_W  = 172
        ROW_H    = 19
        PAD      = 6
        panel_h  = 22 + len(rows) * ROW_H + PAD

        px = SCREEN_W - PANEL_W - 16
        py = 100 if self.campaign_mode else 80

        panel_s = pygame.Surface((PANEL_W, panel_h), pygame.SRCALPHA)
        panel_s.fill((12, 10, 22, 180))
        surf.blit(panel_s, (px, py))
        pygame.draw.rect(surf, (70, 60, 120), (px, py, PANEL_W, panel_h), 1, border_radius=4)

        title_s = self._wpn_font_title.render(T("weapons_title"), True, (180, 160, 255))
        surf.blit(title_s, (px + PAD, py + 4))

        for i, (label, value_str) in enumerate(rows):
            ry = py + 22 + i * ROW_H
            lbl_s = self._wpn_font_row.render(str(label), True, (200, 195, 240))
            surf.blit(lbl_s, (px + PAD, ry))
            val_s = self._wpn_font_row.render(value_str, True, C_YELLOW)
            surf.blit(val_s, (px + PANEL_W - val_s.get_width() - PAD, ry))

    # -----------------------------------------------------------------------
    def _draw_boss_alert(self, surf):
        """Ekranın ortasında kırmızı yanıp sönen BOSS FIGHT! bildirimi."""
        t      = self.boss_alert_timer
        alpha  = int(min(255, t * 3))
        # Arka plan şeridi
        strip = pygame.Surface((SCREEN_W, 80), pygame.SRCALPHA)
        strip.fill((80, 0, 20, min(160, alpha)))
        surf.blit(strip, (0, SCREEN_H // 2 - 40))
        # Yazı (yanıp sönen)
        if (t // 8) % 2 == 0:
            font = pygame.font.SysFont("segoeui", 52, bold=True)
            txt  = font.render(T("boss_fight"), True, (255, 60, 80))
            txt.set_alpha(alpha)
            surf.blit(txt, txt.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))

    # -----------------------------------------------------------------------
    def _draw_pause(self, surf):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surf.blit(overlay, (0, 0))
        t = self.font_big.render(T("paused"), True, C_YELLOW)
        surf.blit(t, (SCREEN_W//2 - t.get_width()//2, SCREEN_H//2 - 30))

    # -----------------------------------------------------------------------
    def _draw_level_completed(self, surf):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surf.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 560, 260)
        panel.center = (SCREEN_W // 2, SCREEN_H // 2)
        panel_s = pygame.Surface((panel.w, panel.h), pygame.SRCALPHA)
        panel_s.fill((*C_UI_BG[:3], 230))
        surf.blit(panel_s, panel.topleft)
        pygame.draw.rect(surf, (120, 100, 220), panel, 2, border_radius=8)

        title = self.font_big.render(T("level_completed"), True, C_YELLOW)
        surf.blit(title, title.get_rect(centerx=panel.centerx, y=panel.y + 38))

        sub = self.font_med.render(
            f"{T('campaign_level', n=self.campaign_level)}  -  "
            f"{T('target_wave', n=campaign_target_wave(self.campaign_level))}",
            True, (200, 195, 240))
        surf.blit(sub, sub.get_rect(centerx=panel.centerx, y=panel.y + 92))

        mx, my = pygame.mouse.get_pos()
        self.btn_next_level.update(mx, my)
        self.btn_completed_menu.update(mx, my)
        self.btn_next_level.label = T("next_level")
        self.btn_completed_menu.label = T("main_menu")
        self.btn_next_level.draw(surf)
        self.btn_completed_menu.draw(surf)

    # -----------------------------------------------------------------------
    def _draw_game_over(self, surf):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surf.blit(overlay, (0, 0))
        elapsed = self.tick // FPS
        mins, secs = divmod(elapsed, 60)
        lines = [
            (T("game_over"),                         self.font_big, C_RED),
            (f"{T('time')}: {mins:02d}:{secs:02d}",  self.font_med, C_WHITE),
            (f"{T('level')}: {self.player.level}",   self.font_med, C_YELLOW),
            (f"{T('kill')}: {self.kills}",            self.font_med, C_ORANGE),
            (f"{T('gold')}: {self.save.total_gold}",self.font_med, C_YELLOW),
            ("",                                      self.font_sm,  C_WHITE),
            (T("restart"),                            self.font_med, (160,160,200)),
        ]
        total_h = sum(f.size("X")[1] + 10 for _, f, _ in lines)
        y = SCREEN_H // 2 - total_h // 2
        for txt, font, color in lines:
            s = font.render(txt, True, color)
            surf.blit(s, (SCREEN_W//2 - s.get_width()//2, y))
            y += font.size("X")[1] + 10


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    Game().run()

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
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum, auto

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

    def update(self, player, enemies, particles, damage_numbers):
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = self.tick
            px, py = player.x, player.y
            for e in enemies:
                if dist((px, py), (e.x, e.y)) < self.radius + e.radius:
                    e.take_damage(self.damage)
                    damage_numbers.append(DamageNumber(e.x, e.y, self.damage, C_PURPLE))
                    for _ in range(4):
                        particles.append(Particle(e.x, e.y, C_PURPLE, speed=2))

    def draw(self, surf, cam_x, cam_y, player, tick):
        px = int(player.x - cam_x)
        py = int(player.y - cam_y)
        pulse = 0.85 + 0.15 * math.sin(tick * 0.15)
        r = int(self.radius * pulse)
        aura_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (180, 80, 255, 30), (r + 1, r + 1), r)
        pygame.draw.circle(aura_surf, (180, 80, 255, 80), (r + 1, r + 1), r, 2)
        surf.blit(aura_surf, (px - r - 1, py - r - 1))


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

    def update(self, player, enemies, particles, damage_numbers):
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

    def update(self, player, enemies, particles, damage_numbers):
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

# ---------------------------------------------------------------------------
# Upgrade seçenekleri
# ---------------------------------------------------------------------------
class UpgradeType(Enum):
    MAX_HP      = auto()
    SPEED       = auto()
    WHIP        = auto()
    ORB         = auto()
    AURA        = auto()
    RECOVERY    = auto()
    ARMOR       = auto()

UPGRADE_DEFS = {
    UpgradeType.MAX_HP:   ("❤ Maks Sağlık",       "+40 maks sağlık",      C_RED),
    UpgradeType.SPEED:    ("⚡ Hız",                "+10% hareket hızı",    C_YELLOW),
    UpgradeType.WHIP:     ("🔥 Kırbaç Güçlendir",  "Hasar & menzil artışı",C_ORANGE),
    UpgradeType.ORB:      ("✨ Orb Güçlendir",      "Yeni orb + hasar",     C_CYAN),
    UpgradeType.AURA:     ("💜 Aura Güçlendir",     "Alan & hasar artışı",  C_PURPLE),
    UpgradeType.RECOVERY: ("💊 Rejenerasyon",       "+1 HP/sn kazanım",     C_GREEN),
    UpgradeType.ARMOR:    ("🛡 Zırh",               "Hasar azaltma",        C_WHITE),
}

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

        # Oyuncuya doğru git
        dx = player.x - self.x
        dy = player.y - self.y
        d = math.hypot(dx, dy)
        if d > 0:
            self.x += (dx / d) * self.speed
            self.y += (dy / d) * self.speed

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

        color = C_WHITE if self.hit_flash > 0 else self.color
        pygame.draw.circle(surf, color, (sx, sy), r)
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
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
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
        self.whip  = WhipWeapon()
        self.orb   = OrbWeapon()
        self.aura  = AuraWeapon()

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

        color = C_WHITE if self.hit_flash > 0 else C_PLAYER
        # Yanıp sönme (dokunulmazlık)
        if self.invincible > 0 and (tick // 4) % 2 == 0:
            color = (200, 200, 200)

        # Gövde
        pygame.draw.circle(surf, C_PLAYER_DARK, (sx, sy), r)
        pygame.draw.circle(surf, color, (sx, sy), r - 3)

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

        title = self.font_big.render("⬆  SEVİYE ATLADINIZ  ⬆", True, C_YELLOW)
        surf.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))
        sub = self.font_med.render("Bir güçlendirme seçin", True, (180, 180, 220))
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

            name, desc, color = UPGRADE_DEFS[ut]

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
                hint = self.font_sm.render("Tıkla veya [1/2/3]", True, (160, 160, 200))
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
    def __init__(self):
        self.timer = 0
        self.wave = 0
        self.wave_timer = 0
        self.base_rate = 120  # frame/spawn
        self.horde_cd = 0

    def update(self, player, enemies, tick):
        self.timer += 1
        self.wave_timer += 1

        # Her 30 saniyede bir wave artar
        wave = tick // (30 * FPS)
        self.wave = wave

        rate = max(20, self.base_rate - wave * 5)

        if self.timer >= rate:
            self.timer = 0
            self._spawn(player, enemies, wave)

        # Her 60 saniyede bir horde
        if tick > 0 and tick % (60 * FPS) == 0:
            for _ in range(20 + wave * 5):
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
# Ana oyun
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Vampire Survivors Clone")
        self.clock = pygame.time.Clock()

        self.font_sm   = pygame.font.SysFont("segoeui", 16)
        self.font_med  = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font_big  = pygame.font.SysFont("segoeui", 36, bold=True)
        self.font_dmg  = pygame.font.SysFont("segoeui", 15, bold=True)

        self.reset()

    def reset(self):
        self.player  = Player(WORLD_W // 2, WORLD_H // 2)
        self.enemies: List[Enemy] = []
        self.enemy_projs: List[Projectile] = []
        self.particles: List[Particle] = []
        self.damage_numbers: List[DamageNumber] = []
        self.xp_gems: List[XPGem] = []
        self.spawn_mgr = SpawnManager()

        self.tick = 0
        self.paused = False
        self.game_over = False
        self.upgrade_screen: Optional[UpgradeScreen] = None
        self.kills = 0

        self.cam_x = self.player.x - SCREEN_W // 2
        self.cam_y = self.player.y - SCREEN_H // 2

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if self.game_over and event.key == pygame.K_r:
                        self.reset()
                        continue

                if self.upgrade_screen:
                    result = self.upgrade_screen.handle_event(event)
                    if result:
                        self._apply_upgrade(result)
                        self.upgrade_screen = None
                        self.paused = False

            if not self.paused and not self.game_over and not self.upgrade_screen:
                self._update()

            self._draw()

    # -----------------------------------------------------------------------
    def _apply_upgrade(self, ut: UpgradeType):
        p = self.player
        if ut == UpgradeType.MAX_HP:
            p.max_hp += 40
            p.hp = min(p.max_hp, p.hp + 40)
        elif ut == UpgradeType.SPEED:
            p.speed_mult *= 1.10
        elif ut == UpgradeType.WHIP:
            p.whip.upgrade()
        elif ut == UpgradeType.ORB:
            p.orb.upgrade()
        elif ut == UpgradeType.AURA:
            p.aura.upgrade()
        elif ut == UpgradeType.RECOVERY:
            p.recovery += 1
        elif ut == UpgradeType.ARMOR:
            p.armor += 2

    # -----------------------------------------------------------------------
    def _update(self):
        self.tick += 1
        keys = pygame.key.get_pressed()
        p = self.player

        p.update(keys, 1 / FPS)

        # Kamera — yumuşak takip
        target_cx = p.x - SCREEN_W // 2
        target_cy = p.y - SCREEN_H // 2
        self.cam_x = lerp(self.cam_x, target_cx, 0.12)
        self.cam_y = lerp(self.cam_y, target_cy, 0.12)

        # Spawn
        self.spawn_mgr.update(p, self.enemies, self.tick)

        # Silah güncellemeleri
        ep = []
        p.whip.update(p, self.enemies, self.particles, self.damage_numbers)
        p.orb.update(p, self.enemies, self.particles, self.damage_numbers)
        p.aura.update(p, self.enemies, self.particles, self.damage_numbers)

        # Düşman güncellemeleri
        new_ep = []
        for e in self.enemies:
            e.update(p, new_ep)
        self.enemy_projs.extend(new_ep)

        # Düşman mermileri
        for proj in self.enemy_projs:
            proj.update()
            if proj.alive:
                if dist((proj.x, proj.y), (p.x, p.y)) < p.radius + proj.size:
                    p.take_damage(proj.damage)
                    for _ in range(4):
                        self.particles.append(Particle(proj.x, proj.y, C_RED, speed=3))
                    proj.alive = False

        # Düşman melee çarpışması
        for e in self.enemies:
            if e.alive and dist((e.x, e.y), (p.x, p.y)) < e.radius + p.radius:
                p.take_damage(e.damage)

        # XP gem toplama
        collected = 0
        for gem in self.xp_gems:
            v = gem.update(p)
            collected += v
        if collected:
            leveled = p.gain_xp(collected)
            if leveled:
                self._trigger_levelup()

        # Ölen düşmanlar -> XP gem, particle
        dead = [e for e in self.enemies if not e.alive]
        for e in dead:
            self.kills += 1
            self.xp_gems.append(XPGem(e.x, e.y, e.xp))
            for _ in range(8):
                self.particles.append(Particle(e.x, e.y, e.color, speed=3, life=40))

        # Temizlik
        self.enemies       = [e for e in self.enemies if e.alive]
        self.enemy_projs   = [p2 for p2 in self.enemy_projs if p2.alive]
        self.particles     = [pt for pt in self.particles if pt.update()]
        self.damage_numbers= [d for d in self.damage_numbers if d.update()]
        self.xp_gems       = [g for g in self.xp_gems if g.alive]

        # Game over
        if p.hp <= 0:
            p.hp = 0
            self.game_over = True

    def _trigger_levelup(self):
        self.paused = True
        available = list(UpgradeType)
        self.upgrade_screen = UpgradeScreen(available)

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

        # XP gem
        for gem in self.xp_gems:
            gem.draw(surf, cx, cy, self.tick)

        # Aura
        self.player.aura.draw(surf, cx, cy, self.player, self.tick)

        # Orb
        self.player.orb.draw(surf, cx, cy, self.player, self.tick)

        # Whip flash
        self.player.whip.draw(surf, cx, cy, self.player)

        # Düşmanlar
        for e in self.enemies:
            e.draw(surf, cx, cy)

        # Düşman mermileri
        for proj in self.enemy_projs:
            proj.draw(surf, cx, cy)

        # Particles
        for pt in self.particles:
            pt.draw(surf, cx, cy)

        # Hasar rakamları
        for dn in self.damage_numbers:
            dn.draw(surf, cx, cy, self.font_dmg)

        # Oyuncu
        self.player.draw(surf, cx, cy, self.tick)

        # UI
        self._draw_ui(surf)

        if self.upgrade_screen:
            self.upgrade_screen.draw(surf)

        if self.paused and not self.upgrade_screen:
            self._draw_pause(surf)

        if self.game_over:
            self._draw_game_over(surf)

        pygame.display.flip()

    def _draw_ui(self, surf):
        p = self.player

        # HP çubuğu
        bar_w = 220
        bx, by = 16, 16
        pygame.draw.rect(surf, C_HP_BG, (bx, by, bar_w, 18), border_radius=4)
        fill = int(bar_w * p.hp / p.max_hp)
        pygame.draw.rect(surf, C_HP, (bx, by, fill, 18), border_radius=4)
        pygame.draw.rect(surf, (200, 200, 200), (bx, by, bar_w, 18), 1, border_radius=4)
        hp_text = self.font_sm.render(f"HP  {p.hp}/{p.max_hp}", True, C_WHITE)
        surf.blit(hp_text, (bx + 4, by + 2))

        # XP çubuğu
        bx2, by2 = 16, 42
        pygame.draw.rect(surf, C_XP_BG, (bx2, by2, bar_w, 12), border_radius=4)
        fill2 = int(bar_w * p.xp / p.xp_needed)
        pygame.draw.rect(surf, C_XP, (bx2, by2, fill2, 12), border_radius=4)
        pygame.draw.rect(surf, (200, 200, 200), (bx2, by2, bar_w, 12), 1, border_radius=4)
        xp_text = self.font_sm.render(f"LV {p.level}  XP {p.xp}/{p.xp_needed}", True, C_WHITE)
        surf.blit(xp_text, (bx2 + 4, by2 - 1))

        # Süre & dalga & kill
        elapsed = self.tick // FPS
        mins, secs = divmod(elapsed, 60)
        wave = self.spawn_mgr.wave
        info = self.font_med.render(
            f"{mins:02d}:{secs:02d}   Dalga {wave + 1}   Kill {self.kills}", True, C_YELLOW)
        surf.blit(info, (SCREEN_W // 2 - info.get_width() // 2, 12))

        # Silah seviyeleri
        wl = self.font_sm.render(
            f"Kırbaç Lv{p.whip.level}  Orb Lv{p.orb.level}  Aura Lv{p.aura.level}"
            f"  Zırh {p.armor}  Regen {p.recovery}",
            True, (180, 180, 220))
        surf.blit(wl, (16, SCREEN_H - 24))

        # Kontrol ipuçları
        hint = self.font_sm.render("WASD: Hareket  P: Duraklat  ESC: Çıkış", True, (100, 100, 140))
        surf.blit(hint, (SCREEN_W - hint.get_width() - 12, SCREEN_H - 24))

    def _draw_pause(self, surf):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surf.blit(overlay, (0, 0))
        t = self.font_big.render("DURAKLATILDI", True, C_YELLOW)
        surf.blit(t, (SCREEN_W // 2 - t.get_width() // 2, SCREEN_H // 2 - 30))

    def _draw_game_over(self, surf):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surf.blit(overlay, (0, 0))

        elapsed = self.tick // FPS
        mins, secs = divmod(elapsed, 60)

        lines = [
            ("GAME OVER", self.font_big, C_RED),
            (f"Süre: {mins:02d}:{secs:02d}", self.font_med, C_WHITE),
            (f"Level: {self.player.level}", self.font_med, C_YELLOW),
            (f"Kill: {self.kills}", self.font_med, C_ORANGE),
            ("", self.font_sm, C_WHITE),
            ("[R] Yeniden Başla   [ESC] Çıkış", self.font_med, (160, 160, 200)),
        ]
        total_h = sum(f.size("X")[1] + 10 for _, f, _ in lines)
        y = SCREEN_H // 2 - total_h // 2
        for txt, font, color in lines:
            s = font.render(txt, True, color)
            surf.blit(s, (SCREEN_W // 2 - s.get_width() // 2, y))
            y += font.size("X")[1] + 10

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    Game().run()

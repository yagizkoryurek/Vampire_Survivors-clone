<p align="center">
  <img src="gameplay.gif" width="900">
</p>
⭐ Enjoyed the game? Leave a star on GitHub to support the project!
# 🧛 Vampire Survivors Clone

Fight hundreds of enemies, evolve powerful weapons and survive endless waves in this Vampire Survivors-inspired game built entirely with Python and Pygame.

---

## 🎮 Gameplay

Survive as long as possible against increasingly difficult enemy waves. Your weapons fire **automatically** — focus on moving, dodging, and choosing the right upgrades.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- **3 Auto-Weapons**
  - 🔥 **Whip** — Slashes the nearest enemy in a cone
  - ✨ **Orb** — Orbiting projectiles that circle the player
  - 💜 **Aura** — Persistent damage field around the player

- **4 Enemy Types**
  - Basic, Fast, Tank, Ranged (with projectile attacks)

- **XP & Level-Up System** — Choose 1 of 3 random upgrades on level-up

- **7 Upgrades** — Max HP, Speed, Whip, Orb, Aura, Regeneration, Armor

- **Wave System** — Difficulty scales every 30 seconds; horde events every 60s

- **Visual Polish** — Particle effects, damage numbers, glow rendering, smooth camera

---

## 🖥️ Requirements

- Python 3.8+
- Pygame 2.x

---

## 🚀 Installation & Run

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/vampire-survivors-clone.git
cd vampire-survivors-clone

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the game
python main.py
```

---

## 🎯 Controls

| Key | Action |
|-----|--------|
| `WASD` / Arrow Keys | Move |
| `P` | Pause / Resume |
| `1` / `2` / `3` | Select upgrade on level-up |
| `R` | Restart (after Game Over) |
| `ESC` | Quit |

---

## 🏆 How to Play

1. Move to avoid enemies — they always chase you
2. Your weapons fire automatically
3. Kill enemies → collect XP gems → level up → choose upgrades
4. Survive as long as possible — waves get harder every 30 seconds
5. Every 60 seconds, a **horde event** spawns a massive wave

---

## 📁 Project Structure

```
vampire-survivors-clone/
├── main.py          # Full game source (single-file architecture)
├── requirements.txt # Python dependencies
├── README.md        # This file
└── LICENSE          # MIT License
```

---

## 🛠️ Built With

- [Python](https://python.org) — Core language
- [Pygame](https://pygame.org) — Game framework

---

## 📜 License

MIT License — free to use, modify, and distribute.

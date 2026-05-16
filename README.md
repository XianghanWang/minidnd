# Mini Dungeon

A 2D top-down dungeon crawler inspired by [Micro Dungeon](https://boardgamegeek.com/boardgame/332306/micro-dungeon).
Bold black ink illustrations on white cards, laid on a dark table. All art drawn with Pygame primitives — zero external assets.

## Requirements
- Python 3.10+
- Pygame 2.5+

## Install & Run
```bash
pip install -r requirements.txt
python src/main.py
```

## How to Play
1. Choose game mode (Single Player or Multiplayer)
2. Select your character(s)
3. Explore the dungeon by moving to edge connection points — new cards appear as you explore
4. Fight monsters, open chests, level up, find the boss room!

### Controls
- **Click** highlighted tiles to move, attack, open doors/chests
- **1 / 2 / 3** — Use character skills (then click target if needed)
- **H** — Use a healing potion (costs 1 AP, heals 5 HP, once per turn)
- **Space** — Reset camera to current player
- **Right-click drag** — Pan camera
- **ESC** — Return to menu

## Characters

| Character | ATK | HP | AP | Speed | Range | Style |
|-----------|-----|----|----|-------|-------|-------|
| Warrior   | 3   | 10 | 3  | 2     | 1     | Tank  |
| Wizard    | 5   | 6  | 2  | 1     | 1     | Glass cannon |
| Hunter    | 4   | 7  | 3  | 3     | 3     | Fast & ranged |

### Skills

**Warrior**
- **Shield Bash** (1 AP, CD 3): Stun a monster for 1 turn, deal 2 dmg
- **War Cry** (1 AP, CD 4): +2 ATK for 2 turns

**Wizard**
- **Fireball** (2 AP, CD 4): AoE damage that scales with level (+1 dmg/level)
- **Heal** (1 AP, CD 3): Heal self for 6 HP
- **Teleport** (1 AP, CD 3): Blink to any walkable tile within range 4

**Hunter**
- **Multi-Shot** (2 AP, CD 3): Hit all monsters in range for 3 dmg
- **Trap** (1 AP, CD 4): Place a trap on adjacent tile (5 dmg when triggered)

## Monsters

| Monster  | ATK | HP | Speed | AP | Territory | XP |
|----------|-----|----|-------|----|-----------|----|
| Bat      | 1   | 4  | 3     | 2  | 5         | 5  |
| Goblin   | 2   | 6  | 2     | 2  | 4         | 8  |
| Slime    | 2   | 10 | 1     | 1  | 3         | 10 |
| Skeleton | 3   | 8  | 1     | 1  | 3         | 12 |
| Spider   | 3   | 7  | 2     | 2  | 4         | 15 |
| Orc      | 4   | 12 | 1     | 2  | 5         | 20 |
| Wraith   | 5   | 9  | 2     | 2  | 5         | 25 |
| **Boss** | 10  | 80 | 1     | 4  | 12        | —  |

The Boss is a 2×2 tile monster with attack range 3 and three skills:
- **Dark Bolt**: Ranged attack (range 4, 8 dmg)
- **Stomp**: AoE shockwave (5 dmg to all within range 2)
- **Summon**: Spawns a Skeleton minion when guards thin out

### Elite Monsters
Boss room guards spawn as **elite** variants: 1.5× HP/ATK, always aggressive, 2+ AP, and patrol the arena.

## Boss Room
- Appears after 8 cards drawn
- Spans a **3×3 card grid** (15×21 tiles) — a large arena
- Features: 4 stone pillars for cover, corner alcoves with chests, center arena ring
- Entry gated by a door that **locks** once you enter — no escape!
- 6 elite guard monsters + the Boss

## Progression
- **XP & Levels**: Gain XP from kills (shared among alive players). Level up at 25×level XP.
- **Level Up**: +1 ATK, +2 Max HP, full heal. Golden ring animation plays.
- **Fireball Scaling**: Wizard's Fireball gains +1 damage and +0.5 splash per level.
- **Potions**: Found from chests/drops. Stored up to 5. Press H to use (heals 5 HP, 1 AP).

## Visual Style
Inspired by the Micro Dungeon PnP card game:
- **Pure black table** background
- **White cards** with rough/torn edges and fuzzy paper fibers
- **Bold black ink** illustrations (high contrast)
- **Colored cube tokens** for HP/AP (red = health, green = action points)
- **Character card HUD** at bottom with ink portrait, stat icons, and cube indicators
- **Floating message log** above HUD

## Project Structure

```
minidnd/
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── spec/                   # Game design specs
│   ├── game-overview.md
│   ├── characters.md
│   ├── dungeon-cards.md
│   ├── combat-and-turns.md
│   ├── items-and-loot.md
│   └── ui-and-style.md
├── src/                    # Game source code
│   ├── main.py             # Entry point, game loop, state machine
│   ├── constants.py        # All config, stats, colors, strings
│   ├── dungeon.py          # Dungeon card generation + boss room
│   ├── entities.py         # Player and Monster classes
│   ├── world.py            # World map (card placement, expansion)
│   ├── game_logic.py       # Turn system, combat, skills, monster AI
│   └── renderer.py         # All rendering (Pygame drawing)
└── .copilot/               # Copilot instructions
```

## Architecture

```
main.py (Game class)
  ├── State machine: Menu → Mode Select → Char Select → Playing → Game Over
  ├── Input handling (mouse clicks, keyboard, skill targeting)
  └── Update loop (monster turn timer)

renderer.py (Renderer class + Camera)
  ├── Micro Dungeon PnP card visual style
  ├── Character card HUD with ink portraits
  └── Combat animations (claw, fireball, level-up)

game_logic.py (GameLogic class)
  ├── Turn management (player phase ↔ monster phase)
  ├── Skills: AoE, stun, buff, heal, teleport, trap, multi-shot
  ├── Boss AI: ranged attacks, AoE stomp, minion summoning
  ├── Monster AI: patrol, chase, territory, multi-AP turns
  └── Elite monster system (boss room guards)

world.py (WorldMap class)
  ├── Manages placed dungeon cards
  ├── Boss room: 3×3 card grid with locking door
  └── Map expansion at connection points

dungeon.py (DungeonCard + DungeonDeck)
  ├── Procedural card generation (5×7 tiles)
  └── Boss room generation (15×21 arena)

entities.py (Player + Monster)
  ├── Stats, inventory, skills, cooldowns, buffs
  ├── Multi-tile boss (2×2), elite flag, patrol waypoints
  └── Loot generation
```


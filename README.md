# Mini Dungeon

A 2D top-down board game style dungeon crawler for desktop PC.
Hand-drawn ink-on-parchment art style. Mouse-click operated.

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
3. Explore the dungeon by moving to edge connection points
4. Fight monsters, open chests, find the boss!

### Controls
- Click highlighted tiles to move, attack, open doors/chests
- **H** — Use a healing potion (costs 1 AP, heals 5 HP, once per turn)
- **Space** — Reset camera to current player
- **Right-click drag** — Pan camera
- **ESC** — Return to menu

## Characters
| Character | ATK | HP | AP | Speed | Style |
|-----------|-----|----|----|-------|-------|
| Warrior   | 3   | 10 | 3  | 2     | Tank  |
| Wizard    | 5   | 6  | 2  | 1     | Glass cannon |
| Hunter    | 4   | 7  | 3  | 3     | Fast & balanced |

## Monsters
| Monster  | ATK | HP | Speed | Territory | XP |
|----------|-----|----|-------|-----------|----|
| Bat      | 1   | 4  | 3     | 5         | 5  |
| Goblin   | 2   | 6  | 2     | 4         | 8  |
| Slime    | 2   | 10 | 1     | 3         | 10 |
| Skeleton | 3   | 8  | 1     | 3         | 12 |
| Spider   | 3   | 7  | 2     | 4         | 15 |
| Orc      | 4   | 12 | 1     | 5         | 20 |
| Wraith   | 5   | 9  | 2     | 5         | 25 |
| Boss     | 6   | 35 | 2     | 8         | — |

Weaker monsters (Goblin, Bat) appear more frequently. Stronger monsters (Orc, Wraith) are rare.
Killing monsters awards shared XP, gold (ATK×5), and a 30% chance of loot drops.

## Progression
- **XP & Levels**: Gain XP from kills (shared among alive players). Level up at 25×level XP.
- **Level Up**: +1 ATK, +2 Max HP, full heal. Golden ring animation plays.
- **Potions**: Found from chests/drops. Stored up to 5. Press H to use (heals 5 HP, 1 AP).
- **Boss**: Appears after 8 cards drawn. Defeating the boss wins the game.

## Project Structure

```
minidnd/
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── spec/                   # Game design requirements & specs
│   ├── game-overview.md
│   ├── characters.md
│   ├── dungeon-cards.md
│   ├── combat-and-turns.md
│   ├── items-and-loot.md
│   └── ui-and-style.md
├── src/                    # Game source code
│   ├── main.py             # Entry point, game loop, state machine
│   ├── constants.py        # All config, stats, colors, strings
│   ├── dungeon.py          # Dungeon card generation (7×11 procedural)
│   ├── entities.py         # Player and Monster classes, loot
│   ├── world.py            # World map (card placement, expansion)
│   ├── game_logic.py       # Turn system, combat, monster AI
│   └── renderer.py         # All rendering (Pygame drawing)
├── .copilot/               # Copilot instructions
└── .squad/                 # Squad multi-agent config
```

## Architecture

```
main.py (Game class)
  ├── State machine: Menu → Mode Select → Char Select → Playing → Game Over
  ├── Input handling (mouse clicks, keyboard)
  └── Update loop (monster turn timer)

renderer.py (Renderer class + Camera)
  └── Draws everything based on current state

game_logic.py (GameLogic class)
  ├── Turn management (player phase ↔ monster phase)
  ├── Action execution (move, attack, open door/chest)
  └── Monster AI (move toward / attack nearest player)

world.py (WorldMap class)
  ├── Manages placed dungeon cards
  ├── Tile queries (walkable, door, chest)
  └── Map expansion at connection points

dungeon.py (DungeonCard + DungeonDeck)
  ├── Procedural card generation
  └── Boss card after 20 draws

entities.py (Player + Monster)
  ├── Stats, inventory, damage
  └── Loot generation
```


# Source Code Guide

## Modules

### `main.py` — Entry Point
- `Game` class: manages the game state machine and main loop
- States: menu → mode_select → char_select → playing → game_over
- Handles all input routing: mouse clicks, keyboard shortcuts, skill targeting
- Armed skill state for click-to-target skill usage

### `constants.py` — Configuration
- Screen/tile dimensions (1280×720, 48px tiles)
- Micro Dungeon color palette (black table, white cards, bold ink)
- Character stats (Warrior, Wizard, Hunter) with attack ranges
- Monster stats (7 types + Boss) with territory, AP, and size
- Skill definitions per character class and Boss skills
- Item/loot table with weapons (including ranged Bow/Long Bow)
- Boss room grid dimensions (3×3 cards)
- All UI strings (English, localization-ready)

### `dungeon.py` — Card Generation
- `DungeonCard`: generates a 5×7 tile grid with paths, rooms, doors, chests, monsters
- `DungeonDeck`: manages draw count, triggers boss room after 8 draws
- `generate_boss_cards()`: creates a 3×3 card boss room (15×21 tiles) with pillars, alcoves, arena ring, entry corridor, and clear path from door
- Connection points at center of each edge ensure cards can connect
- Door placement enforces minimum Manhattan distance of 3

### `entities.py` — Game Entities
- `Player`: stats, inventory, equipment, damage/healing, XP/level system, storable potions, skills with cooldowns and active buffs
- `Monster`: stats, AI states (sleeping/chasing/returning/patrolling), buff system, stun mechanic, elite flag, patrol waypoints, skill cooldowns
- Multi-tile boss (2×2) with `occupies_tile()`, `get_occupied_tiles()`, `get_adjacent_tiles()`
- `generate_loot()`: weighted random item from loot table

### `world.py` — World Map
- `WorldMap`: holds all placed cards and their contents
- Converts between world coordinates and card-local coordinates
- Expands map only at connection points (center of card edges)
- `_try_place_boss_room()`: places 3×3 boss room grid
- `check_boss_room_entry()`: locks boss room door when player enters
- Tracks opened doors/chests, boss room metadata
- Prevents expansion from boss sub-cards

### `game_logic.py` — Game Rules
- `GameLogic`: turn management, action validation, monster AI
- Player actions: move, attack (with range support), open_door, open_chest, skip, use_potion
- Character skills: Shield Bash (stun), War Cry (ATK buff), Fireball (AoE, scales with level), Heal, Teleport, Multi-Shot, Trap
- Boss skills: Dark Bolt (ranged), Stomp (AoE), Summon (spawn minion)
- Boss AI: prioritizes skills based on player distance and guard count
- Monster AI: multi-AP turns, territory-aware chasing, patrol waypoints (elite), stun mechanic
- Trap system: placed traps trigger when monsters walk over them
- BFS-based movement validation
- Elite monster spawning in boss room (1.5× stats, always aggressive)
- Round tracking with monster buff every 5 rounds

### `renderer.py` — Drawing
- `Camera`: pans view centered on current player, right-click drag to pan
- `Renderer`: Micro Dungeon PnP visual style
  - Dark table texture (near-black with subtle noise)
  - White cards with torn/rough edges, fuzzy paper fibers, ink borders
  - Per-type monster ink illustrations (Goblin, Skeleton, Orc, Spider, Bat, Slime, Wraith, Boss)
  - Circular player tokens with class icons (sword, star, bow)
  - Character card HUD with ink portrait, stat grid, red/green cube indicators
  - Floating message log above HUD
  - Combat animations: claw scratch, fireball explosion, trap trigger, level-up ring
  - Ambient dust particles

## Key Design Decisions
- No external art assets — all visuals drawn with Pygame primitives
- Procedural dungeon generation — infinite replayability
- Simple state machine — easy to add new screens
- All strings in `STRINGS` dict — ready for i18n
- Boss room as 3×3 card grid for epic arena feel
- Elite monster system for boss room difficulty scaling
- Micro Dungeon PnP aesthetic: black table, white cards, bold ink, torn edges

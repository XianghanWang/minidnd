# Source Code Guide

## Modules

### `main.py` — Entry Point
- `Game` class: manages the game state machine and main loop
- States: menu → mode_select → char_select → playing → game_over
- Handles all input routing and delegates to appropriate handlers

### `constants.py` — Configuration
- Screen/tile dimensions
- Color palette (ink-on-parchment style)
- Character stats, monster stats, item definitions
- Loot table with drop weights
- Game rules (boss threshold, buff interval, max players)
- All UI strings (English, localization-ready)

### `dungeon.py` — Card Generation
- `DungeonCard`: generates a 7×11 tile grid with paths, rooms, doors, chests, monsters
- `DungeonDeck`: manages draw count, triggers boss card after 20 draws
- Connection points at center of each edge ensure cards can connect

### `entities.py` — Game Entities
- `Player`: stats, inventory, equipment, damage/healing, XP/level system, storable potions
- `Monster`: stats, AI state, buff system
- `generate_loot()`: weighted random item from loot table

### `world.py` — World Map
- `WorldMap`: holds all placed cards and their contents
- Converts between world coordinates and card-local coordinates
- Expands map only at connection points (center of card edges)
- Tracks opened doors/chests

### `game_logic.py` — Game Rules
- `GameLogic`: turn management, action validation, monster AI
- Player actions: move, attack (with range support), open_door, open_chest, skip, use_potion (H key)
- BFS-based movement: players cannot move through walls, monsters, or other players
- Monster AI: multi-AP turns (move AND attack), territory-aware chasing
- Attack range: Hunter has range 3; Bow/Long Bow weapons grant ranged attacks
- Round tracking with monster buff every 5 rounds
- XP shared among alive players on monster kill; gold + loot drops on kill
- Score summary for game over screen

### `renderer.py` — Drawing
- `Camera`: pans view centered on current player
- `Renderer`: draws tiles, entities, UI, menus
- Ink-on-parchment style using Pygame primitives (no sprite assets)
- HUD shows level badge, XP bar, potion count alongside HP/AP/stats
- Level-up golden ring animation
- Victory/defeat screen with score breakdown

## Key Design Decisions
- No external art assets — all visuals drawn with Pygame primitives
- Procedural dungeon generation — infinite replayability
- Simple state machine — easy to add new screens
- All strings in `STRINGS` dict — ready for i18n

# Game Overview

## Concept
Mini Dungeon is a 2D top-down dungeon crawler for desktop PC, inspired by the [Micro Dungeon](https://boardgamegeek.com/boardgame/332306/micro-dungeon) PnP card game. Players explore procedurally generated dungeon cards, fight monsters, collect loot, and defeat the boss. All art is drawn with Pygame primitives — zero external assets.

## Platform
- Desktop PC
- Mouse click to operate
- Keyboard shortcuts for skills and potions
- English version (designed for future locale expansion)

## Game Modes
- **Single Player**: One hero explores alone
- **Multiplayer (2-4 players)**: Hot-seat cooperative play

## Map Exploration
- The first map is one dungeon card (5×7 tiles)
- New cards appear ONLY when a player moves to a connection point at the card edge
- This creates a feeling of exploring the unknown dungeon

## Win Condition
- Defeat the Boss monster (appears in a special 3×3 card boss room after 8 cards drawn)

## Lose Condition
- ALL players reach 0 HP

## Scaling
- Every 5 rounds, all monsters get a random buff (+1 attack, +1 health, or +1 speed)
- Wizard's Fireball damage scales with level

# Dungeon Cards

## Card Dimensions
- Each card is **5 rows × 7 columns** (tiles)
- Tile size: 48×48 pixels

## Connection Points
- The center tile of each edge MUST be a road tile
  - Top: (0, 3)
  - Bottom: (4, 3)
  - Left: (2, 0)
  - Right: (2, 6)
- These are the ONLY points where the map expands

## Map Expansion Rules
- Start with exactly 1 card
- When a player moves onto a connection point at a card edge, the adjacent card is generated and attached
- This simulates dungeon exploration — unknown areas only reveal when you walk into them

## Card Contents
- **Road**: Walkable floor tiles (white/cream)
- **Wall**: Impassable (bold black ink)
- **Door**: Blocks passage, costs 1 AP to open
- **Locked Door**: Requires a key + 1 AP to open (~30% of doors)
- **Chest**: Lootable container, costs 1 AP to open
- **Monsters**: 1-4 per card, spawned when card is revealed
- Doors enforce minimum Manhattan distance of 3 between each other

## Generation
- Paths carved from each connection point toward center
- Random rooms (1-3) connected to path network
- Doors placed at narrow passages (spaced apart)
- Monsters placed on road tiles (not on connection points)
- Chests placed on road tiles without monsters (0-2 per card)

## Boss Room
- Special room that appears after **8** normal cards drawn
- Spans a **3×3 card grid** (15 rows × 21 columns total)
- Entry gated by a door that **locks** when the player enters — no escape!

### Boss Room Layout
- 1-tile wall border around entire arena
- 4 stone pillars (2×2 wall blocks) for cover at strategic positions
- Corner alcoves (small rooms with chests) at all 4 corners
- Center raised area border (ring of walls around boss, with cardinal openings)
- Side wall bumps for additional cover during kiting
- Clear 3-wide corridor from entry door into arena

### Boss Room Contents
- **Boss**: 2×2 tile monster placed at center
- **6 elite guard monsters**: Placed strategically around the arena
  - Guards are 1.5× HP/ATK, always aggressive, 2+ AP
  - Guards patrol waypoints when no player is nearby
- **4 chests**: One in each corner alcove

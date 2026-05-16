# Dungeon Cards

## Card Dimensions
- Each card is **7 rows × 11 columns** (tiles)
- Tile size: 48×48 pixels

## Connection Points
- The center tile of each edge MUST be a road tile
  - Top: (0, 5)
  - Bottom: (6, 5)
  - Left: (3, 0)
  - Right: (3, 10)
- These are the ONLY points where the map expands

## Map Expansion Rules
- Start with exactly 1 card
- When a player moves onto a connection point at a card edge, the adjacent card is generated and attached
- This simulates dungeon exploration — unknown areas only reveal when you walk into them

## Card Contents
- **Road**: Walkable floor tiles
- **Wall**: Impassable, drawn with cross-hatch ink pattern
- **Door**: Blocks passage, costs 1 AP to open
- **Locked Door**: Requires a key + 1 AP to open (~30% of doors)
- **Chest**: Lootable container, costs 1 AP to open
- **Monsters**: 1-4 per card, spawned when card is revealed

## Generation
- Paths carved from each connection point toward center
- Random rooms (1-3) connected to path network
- Doors placed at narrow passages
- Monsters placed on road tiles (not on connection points)
- Chests placed on road tiles without monsters (0-2 per card)

## Boss Card
- Special card that appears after 20 normal cards drawn
- Large open room with Boss monster in center
- 4 guard monsters around the boss

# Combat and Turn System

## Turn Order
1. **Player Phase**: Players act in order of speed (highest first)
2. **Monster Phase**: Each monster takes one action
3. Repeat

## Player Actions (each costs 1 Action Point)
- **Move**: Move up to `speed` tiles (Manhattan distance)
- **Attack**: Hit an adjacent monster (deal player's ATK as damage)
- **Open Door**: Open an adjacent door (locked doors need a key)
- **Open Chest**: Loot an adjacent chest (get random item)
- **Skip**: End turn immediately (remaining AP lost)

## Monster Behavior
- Each monster gets exactly 1 action per monster phase
- If adjacent to a player: attack (deal monster's ATK as damage)
- Otherwise: move 1 tile toward nearest player

## Monster Types

| Monster  | Attack | Health | Speed |
|----------|--------|--------|-------|
| Goblin   | 1      | 3      | 2     |
| Skeleton | 2      | 4      | 1     |
| Orc      | 3      | 6      | 1     |
| Boss     | 5      | 20     | 2     |

## Scaling (every 5 rounds)
All alive monsters receive one random buff:
- +1 Attack, OR
- +1 Health, OR
- +1 Speed

## Dead Players
- Dead players are skipped during turn order
- Game continues as long as at least one player is alive

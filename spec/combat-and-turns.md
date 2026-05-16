# Combat and Turn System

## Turn Order
1. **Player Phase**: Players act in order of speed (highest first)
2. **Monster Phase**: Each monster uses all its Action Points (multi-AP turns)
3. Repeat

## Player Actions (each costs 1 AP unless noted)
- **Move**: Move up to `speed` tiles via BFS pathfinding (cannot pass through walls, monsters, or other players)
- **Attack**: Hit a monster within attack range (deal player's ATK as damage)
- **Open Door**: Open an adjacent door (locked doors need a key)
- **Open Chest**: Loot an adjacent chest (get random item)
- **Use Skill**: Activate a character skill (variable AP cost, see Characters spec)
- **Use Potion**: Press H to heal 5 HP (once per turn, costs 1 AP)
- **Skip**: End turn immediately (remaining AP lost)

## Attack Range
- Warrior: melee only (range 1)
- Wizard: melee only (range 1), but has ranged Fireball skill
- Hunter: ranged (range 3), can attack from distance
- Bow/Long Bow weapons grant ranged attacks to any character

## Monster Behavior
- Monsters have **multiple Action Points** (1-4 AP depending on type)
- Each AP allows one action: move OR attack
- **Sleeping**: Idle until a player enters territory or is adjacent → wakes up
- **Chasing**: Moves toward nearest player, attacks if adjacent
- **Returning**: Returns home if player leaves territory, then sleeps
- **Patrolling** (elite only): Walks between waypoints when no player nearby

## Monster Types

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

## Boss
- **Size**: 2×2 tiles
- **Attack Range**: 3 (can hit from distance)
- **Skills** (with cooldowns):
  - **Dark Bolt** (CD 2): Ranged attack, range 4, 8 damage. Used when player is in range.
  - **Stomp** (CD 3): AoE shockwave, 5 damage to all players within range 2. Used when player is adjacent.
  - **Summon** (CD 5): Spawns an elite Skeleton minion nearby. Used when guards are thinning out (< 3 alive).
- Boss AI prioritizes skills over basic attacks

## Elite Monsters
Boss room guards are **elite** variants:
- 1.5× base HP and ATK
- Always start in chasing/patrolling state (never sleep)
- Minimum 2 AP per turn
- Patrol between waypoints when idle

## Scaling (every 5 rounds)
All alive monsters receive one random buff:
- +1 Attack, OR
- +1 Health, OR
- +1 Speed

## Trap System
- Hunter's Trap skill places a trap on an adjacent tile
- Traps trigger when any monster steps on the tile
- Deals 5 damage to the triggering monster
- Traps are visible on the dungeon floor

## Dead Players
- Dead players are skipped during turn order
- Game continues as long as at least one player is alive

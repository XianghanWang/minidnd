# Characters

## Design Principles
- 3 character types: Warrior, Wizard, Hunter
- Each has different play styles via stat differences and unique skills

## Stats

| Character | Attack | Health | Action Points | Speed | Range | Color |
|-----------|--------|--------|---------------|-------|-------|-------|
| Warrior   | 3      | 10     | 3             | 2     | 1     | Blue  |
| Wizard    | 5      | 6      | 2             | 1     | 1     | Purple |
| Hunter    | 4      | 7      | 3             | 3     | 3     | Green |

## Skills

### Warrior
- **Shield Bash** (1 AP, CD 3, Key 1): Stun a monster for 1 turn, deal 2 damage
- **War Cry** (1 AP, CD 4, Key 2): +2 ATK buff for 2 turns

### Wizard
- **Fireball** (2 AP, CD 4, Key 1): AoE ranged attack (range 3). Base 4 dmg + 1/level, splash 2 + 0.5/level
- **Heal** (1 AP, CD 3, Key 2): Heal self for 6 HP
- **Teleport** (1 AP, CD 3, Key 3): Blink to any walkable tile within range 4

### Hunter
- **Multi-Shot** (2 AP, CD 3, Key 1): Hit ALL monsters in range for 3 dmg
- **Trap** (1 AP, CD 4, Key 2): Place a trap on adjacent tile (5 dmg when monster steps on it)

## Descriptions
- **Warrior**: Strong and tough. A frontline fighter. High HP, moderate damage. Shield Bash provides crowd control.
- **Wizard**: Powerful spells but fragile. Highest attack, lowest health and speed. Fireball scales with level. Teleport compensates for low speed.
- **Hunter**: Fast and versatile. Strikes swiftly. Best speed and range, balanced stats. Multi-Shot for crowd clear.

## Notes
- Speed determines turn order in multiplayer (highest goes first)
- Speed determines movement range per move action (tiles reachable = speed)
- Action Points replenish at the start of each turn
- Skills have cooldowns that count down each turn
- Level up: +1 ATK, +2 Max HP, full heal

# Items and Loot

## Obtaining Items
- Open a chest (1 AP) to receive a random item from the loot table
- Items are applied immediately (potions heal, weapons equip, keys add to inventory)

## Item Types

### Weapons (auto-equip if better)
| Item   | Attack Bonus | Weight |
|--------|-------------|--------|
| Dagger | +1          | 15%    |
| Sword  | +2          | 10%    |
| Staff  | +3          | 5%     |

### Consumables
| Item           | Effect       | Weight |
|----------------|-------------|--------|
| Health Potion  | Restore 3 HP | 25%    |
| Greater Potion | Restore 5 HP | 10%    |

### Utility
| Item | Effect              | Weight |
|------|---------------------|--------|
| Key  | Opens locked doors  | 15%    |

### Treasure (score)
| Item | Value   | Weight |
|------|---------|--------|
| Gold | 10 gold | 15%    |
| Gem  | 25 gold | 5%     |

## Weapon Equip Rules
- Only one weapon equipped at a time
- Auto-equips if no weapon or if new weapon is strictly better
- Extra weapons go to inventory (not used currently)

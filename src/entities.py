"""Mini Dungeon - Entity classes (Players, Monsters)"""

import random
from constants import CHARACTERS, MONSTERS, ITEMS, LOOT_TABLE, SKILLS


class Player:
    """A player character."""

    def __init__(self, player_id, character_type):
        self.player_id = player_id
        self.character_type = character_type
        stats = CHARACTERS[character_type]
        self.base_attack = stats["attack"]
        self.attack = stats["attack"]
        self.health = stats["health"]
        self.max_health = stats["max_health"]
        self.max_action_points = stats["action_points"]
        self.action_points = stats["action_points"]
        self.speed = stats["speed"]
        self.color = stats["color"]
        self.attack_range = stats.get("attack_range", 1)
        self.base_attack_range = self.attack_range

        # Position on the world grid
        self.world_col = 0

        # Inventory
        self.inventory = []
        self.keys = 0
        self.gold = 0
        self.weapon = None
        self.damage_flash = 0

        # Level / XP
        self.level = 1
        self.xp = 0
        self.xp_to_next = 25  # level * 25
        self.monsters_killed = 0

        # Potions
        self.potions = 0
        self.max_potions = 5
        self.used_potion_this_turn = False

        # Skills
        self.skills = SKILLS.get(character_type, [])
        self.skill_cooldowns = [0] * len(self.skills)  # 0 = ready
        self.active_buffs = []  # list of {"type": str, "amount": int, "turns_left": int}

    def start_turn(self):
        """Reset action points at start of turn."""
        self.action_points = self.max_action_points
        self.used_potion_this_turn = False
        # Reduce skill cooldowns
        for i in range(len(self.skill_cooldowns)):
            if self.skill_cooldowns[i] > 0:
                self.skill_cooldowns[i] -= 1
        # Tick buffs
        expired = []
        for buff in self.active_buffs:
            buff["turns_left"] -= 1
            if buff["turns_left"] <= 0:
                expired.append(buff)
        for buff in expired:
            if buff["type"] == "buff_attack":
                self.attack -= buff["amount"]
            self.active_buffs.remove(buff)

    def use_action_point(self):
        """Use one action point. Returns True if successful."""
        if self.action_points > 0:
            self.action_points -= 1
            return True
        return False

    def take_damage(self, damage):
        """Take damage. Returns True if still alive."""
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.damage_flash = 10
        return self.health > 0

    def heal(self, amount):
        """Heal by amount, capped at max health."""
        self.health = min(self.health + amount, self.max_health)

    def equip_weapon(self, weapon_name):
        """Equip a weapon, updating attack stat."""
        item = ITEMS[weapon_name]
        self.weapon = weapon_name
        self.attack = self.base_attack + item["attack_bonus"]
        # Update range if weapon provides it
        weapon_range = item.get("attack_range", 0)
        if weapon_range > 0:
            self.attack_range = weapon_range
        else:
            self.attack_range = self.base_attack_range

    def add_item(self, item_name):
        """Add an item to inventory and apply its effects."""
        item = ITEMS[item_name]
        if item["type"] == "weapon":
            # Auto-equip if better than current
            if self.weapon is None:
                self.equip_weapon(item_name)
            elif ITEMS[item_name]["attack_bonus"] > ITEMS[self.weapon]["attack_bonus"]:
                self.equip_weapon(item_name)
            else:
                self.inventory.append(item_name)
        elif item["type"] == "potion":
            if self.potions < self.max_potions:
                self.potions += 1
            else:
                self.heal(item["heal"])
        elif item["type"] == "key":
            self.keys += 1
        elif item["type"] == "treasure":
            self.gold += item["value"]

    def is_alive(self):
        return self.health > 0

    def gain_xp(self, amount):
        """Gain XP and check for level up. Returns True if leveled up."""
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self._level_up()
            return True
        return False

    def _level_up(self):
        """Level up: increase stats."""
        self.xp -= self.xp_to_next
        self.level += 1
        self.xp_to_next = self.level * 25
        self.base_attack += 1
        self.attack += 1
        self.max_health += 2
        self.health = self.max_health  # Full heal on level up

    def use_potion(self):
        """Use a healing potion. Returns True if used."""
        if self.potions > 0 and not self.used_potion_this_turn:
            self.potions -= 1
            self.heal(5)
            self.used_potion_this_turn = True
            return True
        return False

    def can_use_skill(self, skill_index):
        """Check if a skill can be used (enough AP + off cooldown)."""
        if skill_index >= len(self.skills):
            return False
        skill = self.skills[skill_index]
        return (self.action_points >= skill["ap_cost"] and
                self.skill_cooldowns[skill_index] == 0)


class Monster:
    """A monster entity on the map."""

    # Monster states
    STATE_SLEEPING = "sleeping"
    STATE_CHASING = "chasing"
    STATE_RETURNING = "returning"

    def __init__(self, monster_type, world_row, world_col):
        self.monster_type = monster_type
        stats = MONSTERS[monster_type]
        self.attack = stats["attack"]
        self.health = stats["health"]
        self.max_health = stats["health"]
        self.speed = stats["speed"]
        self.color = stats["color"]
        self.territory_range = stats.get("territory", 4)
        self.world_row = world_row
        self.world_col = world_col
        self.home_row = world_row
        self.home_col = world_col
        self.state = Monster.STATE_SLEEPING
        self.has_acted = False
        self.action_points = stats.get("action_points", 1)
        self.max_action_points = self.action_points
        self.damage_flash = 0
        self.stun_turns = 0

    def take_damage(self, damage):
        """Take damage. Returns True if still alive."""
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.damage_flash = 10
        return self.health > 0

    def is_alive(self):
        return self.health > 0

    def buff(self):
        """Apply a random buff to this monster."""
        buff_type = random.choice(["attack", "health", "speed"])
        if buff_type == "attack":
            self.attack += 1
        elif buff_type == "health":
            self.health += 1
            self.max_health += 1
        else:
            self.speed += 1

    def reset_turn(self):
        """Reset action state for new turn."""
        self.has_acted = False
        self.action_points = self.max_action_points

    def wake_up(self):
        """Wake the monster (e.g. when hit or player enters territory)."""
        if self.state == Monster.STATE_SLEEPING:
            self.state = Monster.STATE_CHASING

    def is_in_territory(self, row, col):
        """Check if a position is within this monster's territory."""
        dist = abs(row - self.home_row) + abs(col - self.home_col)
        return dist <= self.territory_range

    def dist_from_home(self):
        """Manhattan distance from home position."""
        return abs(self.world_row - self.home_row) + abs(self.world_col - self.home_col)


def generate_loot():
    """Generate a random loot item based on loot table weights."""
    items = list(LOOT_TABLE.keys())
    weights = list(LOOT_TABLE.values())
    return random.choices(items, weights=weights, k=1)[0]

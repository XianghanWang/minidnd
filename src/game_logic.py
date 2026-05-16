"""Mini Dungeon - Game Logic (Turn system, Combat, AI)"""

import random
from collections import deque
from constants import (
    MONSTER_BUFF_INTERVAL, TILE_ROAD, ACTION_MOVE, ACTION_ATTACK,
    ACTION_OPEN_DOOR, ACTION_OPEN_CHEST, ACTION_SKIP, MONSTERS
)
from entities import generate_loot


class GameLogic:
    """Manages game turns, combat, and monster AI."""

    def __init__(self, world, players):
        self.world = world
        self.players = players
        self.current_player_index = 0
        self.round_number = 1
        self.is_player_phase = True
        self.is_monster_phase = False
        self.monster_action_index = 0
        self.game_over = False
        self.game_won = False
        self.message_log = []
        self.pending_animations = []  # Queued animation events for renderer
        self.traps = []  # list of {"row": int, "col": int, "damage": int, "owner": player}

        # Sort players by speed (highest first)
        self.players.sort(key=lambda p: p.speed, reverse=True)

        # Start first player's turn
        if self.players:
            self.players[0].start_turn()

    def get_current_player(self):
        """Get the current active player."""
        if self.is_player_phase and self.players:
            return self.players[self.current_player_index]
        return None

    def log_message(self, msg):
        """Add a message to the log."""
        self.message_log.append(msg)
        if len(self.message_log) > 8:
            self.message_log.pop(0)

    def player_move(self, player, target_row, target_col):
        """Attempt to move player to target position."""
        if not player.use_action_point():
            return False

        # Validate target is reachable via BFS
        valid_tiles = self.get_valid_move_tiles(player)
        if (target_row, target_col) not in valid_tiles:
            player.action_points += 1  # Refund
            return False

        player.world_row = target_row
        player.world_col = target_col

        # Check if at edge - expand map
        self.world.check_edge_and_expand(target_row, target_col)

        self.log_message(f"{player.character_type} moved to ({target_row}, {target_col})")
        return True

    def player_attack(self, player, target_row, target_col):
        """Player attacks a monster at target position."""
        if not player.use_action_point():
            return False

        # Check within attack range
        dist = abs(target_row - player.world_row) + abs(target_col - player.world_col)
        if dist > player.attack_range or dist < 1:
            player.action_points += 1
            return False

        monster = self.world.get_monster_at(target_row, target_col)
        if not monster:
            player.action_points += 1
            return False

        # Wake the monster if sleeping
        monster.wake_up()

        # Queue attack animation
        self.pending_animations.append({
            "type": "player_slash",
            "world_row": target_row,
            "world_col": target_col,
            "damage": player.attack,
        })

        # Deal damage
        monster.take_damage(player.attack)
        self.log_message(
            f"{player.character_type} hits {monster.monster_type} for {player.attack} dmg!"
        )

        if not monster.is_alive():
            self._handle_monster_death(player, monster, target_row, target_col)

        return True

    def player_open_door(self, player, target_row, target_col):
        """Player opens a door."""
        if not player.use_action_point():
            return False

        dist = abs(target_row - player.world_row) + abs(target_col - player.world_col)
        if dist != 1:
            player.action_points += 1
            return False

        if not self.world.is_door(target_row, target_col):
            player.action_points += 1
            return False

        # Check if locked and player has key
        if self.world.is_locked_door(target_row, target_col):
            if player.keys <= 0:
                player.action_points += 1
                self.log_message("Door is locked! Need a key.")
                return False
            player.keys -= 1
            self.log_message(f"{player.character_type} used a key!")

        self.world.open_door(target_row, target_col)
        self.log_message(f"{player.character_type} opened a door!")
        return True

    def player_open_chest(self, player, target_row, target_col):
        """Player opens a chest."""
        if not player.use_action_point():
            return False

        dist = abs(target_row - player.world_row) + abs(target_col - player.world_col)
        if dist != 1:
            player.action_points += 1
            return False

        if not self.world.is_chest(target_row, target_col):
            player.action_points += 1
            return False

        self.world.open_chest(target_row, target_col)
        loot = generate_loot()
        player.add_item(loot)
        self.log_message(f"{player.character_type} found: {loot}!")
        return True

    def player_skip(self):
        """Current player skips remaining actions."""
        player = self.get_current_player()
        if player:
            player.action_points = 0
            self.log_message(f"{player.character_type} skips.")
            self._advance_turn()

    def try_advance_turn(self):
        """Check if current player is out of AP and advance."""
        player = self.get_current_player()
        if player and player.action_points <= 0:
            self._advance_turn()

    def _advance_turn(self):
        """Move to next player or monster phase."""
        self.current_player_index += 1
        # Skip dead players
        while (self.current_player_index < len(self.players) and
               not self.players[self.current_player_index].is_alive()):
            self.current_player_index += 1

        if self.current_player_index >= len(self.players):
            # All players done, start monster phase
            self._start_monster_phase()
        else:
            self.players[self.current_player_index].start_turn()

    def _start_monster_phase(self):
        """Begin monster turn."""
        self.is_player_phase = False
        self.is_monster_phase = True
        self.monster_action_index = 0

        # Reset all monster actions
        for monster in self.world.get_alive_monsters():
            monster.reset_turn()

    def process_monster_turn(self):
        """Process one action of current monster. Returns True if more to process."""
        if not self.is_monster_phase:
            return False

        alive_monsters = self.world.get_alive_monsters()
        if self.monster_action_index >= len(alive_monsters):
            self._start_new_round()
            return False

        monster = alive_monsters[self.monster_action_index]
        self._monster_single_action(monster)
        monster.action_points -= 1

        # If monster has no more AP, advance to next monster
        if monster.action_points <= 0:
            self.monster_action_index += 1

        return self.monster_action_index < len(alive_monsters)

    def _monster_single_action(self, monster):
        """Execute one action for a monster (costs 1 AP)."""
        # Stunned monsters skip their turn
        if monster.stun_turns > 0:
            monster.stun_turns -= 1
            monster.action_points = 0
            return

        # Sleeping monsters don't act
        if monster.state == "sleeping":
            adjacent_player = self._get_adjacent_player(monster)
            player_in_territory = self._find_player_in_territory(monster)
            if adjacent_player:
                monster.wake_up()
                self._monster_attack(monster, adjacent_player)
            elif player_in_territory:
                monster.wake_up()
                self._monster_chase(monster, player_in_territory)
            else:
                monster.action_points = 0  # Skip remaining AP
            return

        # Awake monster logic
        adjacent_player = self._get_adjacent_player(monster)
        player_in_territory = self._find_player_in_territory(monster)

        if adjacent_player:
            monster.state = "chasing"
            self._monster_attack(monster, adjacent_player)
        elif player_in_territory:
            monster.state = "chasing"
            self._monster_chase(monster, player_in_territory)
        else:
            monster.state = "returning"
            self._monster_return_home(monster)
            if (monster.world_row == monster.home_row and
                    monster.world_col == monster.home_col):
                monster.state = "sleeping"
                monster.action_points = 0  # Done

    def _get_adjacent_player(self, monster):
        """Find an alive player adjacent to any of the monster's tiles."""
        adjacent_tiles = set(monster.get_adjacent_tiles())
        for player in self.players:
            if player.is_alive():
                if (player.world_row, player.world_col) in adjacent_tiles:
                    return player
        return None

    def _find_player_in_territory(self, monster):
        """Find nearest alive player within monster's territory range from home."""
        nearest = None
        nearest_dist = float('inf')
        for player in self.players:
            if player.is_alive():
                home_dist = (abs(player.world_row - monster.home_row) +
                             abs(player.world_col - monster.home_col))
                if home_dist <= monster.territory_range:
                    # Use nearest occupied tile for multi-tile monsters
                    min_dist = float('inf')
                    for r, c in monster.get_occupied_tiles():
                        d = abs(player.world_row - r) + abs(player.world_col - c)
                        min_dist = min(min_dist, d)
                    if min_dist < nearest_dist:
                        nearest_dist = min_dist
                        nearest = player
        return nearest

    def _monster_attack(self, monster, target_player):
        """Monster attacks an adjacent player."""
        self.pending_animations.append({
            "type": "monster_claw",
            "world_row": target_player.world_row,
            "world_col": target_player.world_col,
            "damage": monster.attack,
        })
        target_player.take_damage(monster.attack)
        self.log_message(
            f"{monster.monster_type} hits {target_player.character_type} "
            f"for {monster.attack} dmg!"
        )
        if not target_player.is_alive():
            self.log_message(f"{target_player.character_type} has fallen!")
            if not any(p.is_alive() for p in self.players):
                self.game_over = True
                self.game_won = False
                self.log_message("All players have fallen...")

    def _monster_chase(self, monster, target_player):
        """Move monster toward target player, staying within territory."""
        dr = target_player.world_row - monster.world_row
        dc = target_player.world_col - monster.world_col

        moves = []
        if abs(dr) >= abs(dc):
            moves = [(1 if dr > 0 else -1, 0), (0, 1 if dc > 0 else -1)]
        else:
            moves = [(0, 1 if dc > 0 else -1), (1 if dr > 0 else -1, 0)]

        for move_r, move_c in moves:
            new_r = monster.world_row + move_r
            new_c = monster.world_col + move_c
            # Must stay within territory
            if not monster.is_in_territory(new_r, new_c):
                continue
            # Check all tiles the monster would occupy after moving
            if not self._can_monster_move_to(monster, new_r, new_c):
                continue
            monster.world_row = new_r
            monster.world_col = new_c
            self._check_trap(monster, new_r, new_c)
            return

    def _monster_return_home(self, monster):
        """Move monster one step toward its home position."""
        dr = monster.home_row - monster.world_row
        dc = monster.home_col - monster.world_col

        if dr == 0 and dc == 0:
            return

        moves = []
        if abs(dr) >= abs(dc):
            moves = [(1 if dr > 0 else -1, 0), (0, 1 if dc > 0 else -1)]
        else:
            moves = [(0, 1 if dc > 0 else -1), (1 if dr > 0 else -1, 0)]

        for move_r, move_c in moves:
            new_r = monster.world_row + move_r
            new_c = monster.world_col + move_c
            if not self._can_monster_move_to(monster, new_r, new_c):
                continue
            monster.world_row = new_r
            monster.world_col = new_c
            self._check_trap(monster, new_r, new_c)
            return

    def _can_monster_move_to(self, monster, new_r, new_c):
        """Check if a monster can move to (new_r, new_c), checking all tiles it occupies."""
        current_tiles = set(monster.get_occupied_tiles())
        for dr in range(monster.size):
            for dc in range(monster.size):
                tr, tc = new_r + dr, new_c + dc
                if (tr, tc) in current_tiles:
                    continue  # Monster already occupies this tile
                if not self.world.is_walkable(tr, tc):
                    return False
                other = self.world.get_monster_at(tr, tc)
                if other and other != monster:
                    return False
                for p in self.players:
                    if p.is_alive() and p.world_row == tr and p.world_col == tc:
                        return False
        return True

    def _start_new_round(self):
        """Start a new round - back to player phase."""
        self.round_number += 1
        self.is_player_phase = True
        self.is_monster_phase = False
        self.current_player_index = 0

        # Buff monsters every N rounds
        if self.round_number % MONSTER_BUFF_INTERVAL == 0:
            for monster in self.world.get_alive_monsters():
                monster.buff()
            self.log_message(f"Round {self.round_number}: Monsters grow stronger!")

        # Start first alive player's turn
        if self.players:
            self.current_player_index = 0
            # Skip dead players
            while (self.current_player_index < len(self.players) and
                   not self.players[self.current_player_index].is_alive()):
                self.current_player_index += 1
            if self.current_player_index < len(self.players):
                self.players[self.current_player_index].start_turn()
            self.log_message(f"Round {self.round_number} begins.")

    def get_valid_move_tiles(self, player):
        """Get tiles the player can reach via step-by-step movement (BFS).
        Cannot pass through tiles occupied by monsters or other players."""
        # Build set of occupied positions (all tiles for multi-tile monsters)
        occupied = set()
        for m in self.world.get_alive_monsters():
            for tile in m.get_occupied_tiles():
                occupied.add(tile)
        for p in self.players:
            if p != player and p.is_alive():
                occupied.add((p.world_row, p.world_col))

        start = (player.world_row, player.world_col)
        visited = {start}
        queue = deque([(start, 0)])  # (position, steps)
        valid = []

        while queue:
            (r, c), steps = queue.popleft()
            if steps >= player.speed:
                continue
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in visited:
                    continue
                visited.add((nr, nc))
                if not self.world.is_walkable(nr, nc):
                    continue
                if (nr, nc) in occupied:
                    continue  # Can't pass through occupied tiles
                valid.append((nr, nc))
                queue.append(((nr, nc), steps + 1))

        return valid

    def get_attackable_monsters(self, player):
        """Get monsters within player's attack range. For multi-tile monsters,
        check distance to the nearest occupied tile."""
        attackable = []
        for monster in self.world.get_alive_monsters():
            min_dist = float('inf')
            for r, c in monster.get_occupied_tiles():
                dist = abs(r - player.world_row) + abs(c - player.world_col)
                min_dist = min(min_dist, dist)
            if 1 <= min_dist <= player.attack_range:
                attackable.append(monster)
        return attackable

    def get_adjacent_monsters(self, player):
        """Get monsters adjacent to player. For multi-tile monsters,
        checks if player is adjacent to any of the monster's tiles."""
        adjacent = []
        for monster in self.world.get_alive_monsters():
            for r, c in monster.get_occupied_tiles():
                dist = abs(r - player.world_row) + abs(c - player.world_col)
                if dist == 1:
                    adjacent.append(monster)
                    break
        return adjacent

    def get_adjacent_doors(self, player):
        """Get door positions adjacent to player."""
        doors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r = player.world_row + dr
            c = player.world_col + dc
            if self.world.is_door(r, c):
                doors.append((r, c))
        return doors

    def get_adjacent_chests(self, player):
        """Get chest positions adjacent to player."""
        chests = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r = player.world_row + dr
            c = player.world_col + dc
            if self.world.is_chest(r, c):
                chests.append((r, c))
        return chests

    def player_use_potion(self, player):
        """Player uses a healing potion. Costs 1 AP."""
        if not player.use_action_point():
            return False
        if player.use_potion():
            self.log_message(f"{player.character_type} used a potion! Healed 5 HP.")
            return True
        else:
            player.action_points += 1  # Refund
            return False

    def _handle_monster_death(self, player, monster, row, col):
        """Handle monster death: XP, loot, boss check."""
        self.log_message(f"{monster.monster_type} defeated!")
        self.pending_animations.append({
            "type": "death_poof",
            "world_row": row, "world_col": col,
        })
        # Award shared XP
        xp_value = MONSTERS.get(monster.monster_type, {}).get("xp", 0)
        if xp_value > 0:
            alive_players = [p for p in self.players if p.is_alive()]
            share = max(1, xp_value // len(alive_players))
            for p in alive_players:
                leveled = p.gain_xp(share)
                if leveled:
                    self.log_message(f"{p.character_type} leveled up to Lv{p.level}!")
                    self.pending_animations.append({
                        "type": "level_up",
                        "world_row": p.world_row, "world_col": p.world_col,
                    })
        player.monsters_killed += 1
        gold_drop = monster.attack * 5
        player.gold += gold_drop
        self.log_message(f"Found {gold_drop} gold!")
        drop_chance = 1.0 if monster.monster_type == "Boss" else 0.3
        if random.random() < drop_chance:
            loot = generate_loot()
            player.add_item(loot)
            self.log_message(f"Dropped: {loot}!")
        if monster.monster_type == "Boss":
            self.game_over = True
            self.game_won = True
            self.log_message("VICTORY! The Boss is defeated!")
        self.world.remove_dead_monsters()

    def _check_trap(self, monster, row, col):
        """Check if monster stepped on a trap."""
        for trap in self.traps[:]:
            if trap["row"] == row and trap["col"] == col:
                monster.take_damage(trap["damage"])
                monster.wake_up()
                self.log_message(f"Trap hits {monster.monster_type} for {trap['damage']} dmg!")
                self.pending_animations.append({
                    "type": "trap_trigger",
                    "world_row": row, "world_col": col,
                    "damage": trap["damage"],
                })
                self.traps.remove(trap)
                if not monster.is_alive():
                    self.log_message(f"{monster.monster_type} defeated by trap!")
                    self.pending_animations.append({
                        "type": "death_poof",
                        "world_row": row, "world_col": col,
                    })
                    xp_value = MONSTERS.get(monster.monster_type, {}).get("xp", 0)
                    if xp_value > 0:
                        alive_players = [p for p in self.players if p.is_alive()]
                        share = max(1, xp_value // len(alive_players))
                        for p in alive_players:
                            leveled = p.gain_xp(share)
                            if leveled:
                                self.log_message(f"{p.character_type} leveled up to Lv{p.level}!")
                    trap["owner"].monsters_killed += 1
                    gold_drop = monster.attack * 5
                    trap["owner"].gold += gold_drop
                    self.world.remove_dead_monsters()
                break

    def use_skill(self, player, skill_index, target_row=None, target_col=None):
        """Execute a skill. Returns True if successful."""
        if not player.can_use_skill(skill_index):
            return False

        skill = player.skills[skill_index]

        # Deduct AP
        for _ in range(skill["ap_cost"]):
            if not player.use_action_point():
                return False

        effect = skill["effect"]

        if effect == "stun":
            dist = abs(target_row - player.world_row) + abs(target_col - player.world_col)
            if dist != 1:
                player.action_points += skill["ap_cost"]
                return False
            monster = self.world.get_monster_at(target_row, target_col)
            if not monster:
                player.action_points += skill["ap_cost"]
                return False
            monster.wake_up()
            monster.take_damage(skill["damage"])
            monster.stun_turns = skill["stun_turns"]
            self.log_message(f"{player.character_type} Shield Bashes {monster.monster_type}! Stunned!")
            self.pending_animations.append({
                "type": "player_slash",
                "world_row": target_row, "world_col": target_col,
                "damage": skill["damage"],
            })
            if not monster.is_alive():
                self._handle_monster_death(player, monster, target_row, target_col)

        elif effect == "buff_attack":
            player.attack += skill["buff_amount"]
            player.active_buffs.append({
                "type": "buff_attack",
                "amount": skill["buff_amount"],
                "turns_left": skill["buff_turns"],
            })
            self.log_message(f"{player.character_type} uses War Cry! ATK +{skill['buff_amount']}!")
            self.pending_animations.append({
                "type": "level_up",
                "world_row": player.world_row, "world_col": player.world_col,
            })

        elif effect == "aoe":
            dist = abs(target_row - player.world_row) + abs(target_col - player.world_col)
            if dist > skill["range"] or dist < 1:
                player.action_points += skill["ap_cost"]
                return False

            primary = self.world.get_monster_at(target_row, target_col)

            self.pending_animations.append({
                "type": "fireball",
                "world_row": target_row, "world_col": target_col,
                "damage": skill["damage"],
            })

            if primary:
                primary.wake_up()
                primary.take_damage(skill["damage"])
                self.log_message(f"Fireball hits {primary.monster_type} for {skill['damage']}!")
                if not primary.is_alive():
                    self._handle_monster_death(player, primary, target_row, target_col)

            splash_range = skill.get("splash_range", 1)
            splash_dmg = skill.get("splash_damage", 0)
            for monster in self.world.get_alive_monsters():
                if monster == primary:
                    continue
                m_dist = abs(monster.world_row - target_row) + abs(monster.world_col - target_col)
                if m_dist <= splash_range:
                    monster.wake_up()
                    monster.take_damage(splash_dmg)
                    self.log_message(f"Splash hits {monster.monster_type} for {splash_dmg}!")
                    self.pending_animations.append({
                        "type": "player_slash",
                        "world_row": monster.world_row, "world_col": monster.world_col,
                        "damage": splash_dmg,
                    })
                    if not monster.is_alive():
                        self._handle_monster_death(player, monster, monster.world_row, monster.world_col)

            self.world.remove_dead_monsters()

        elif effect == "heal":
            heal_amount = skill.get("heal_amount", 5)
            player.heal(heal_amount)
            self.log_message(f"{player.character_type} heals for {heal_amount} HP!")
            self.pending_animations.append({
                "type": "level_up",
                "world_row": player.world_row, "world_col": player.world_col,
            })

        elif effect == "multi_hit":
            targets = self.get_attackable_monsters(player)
            if not targets:
                player.action_points += skill["ap_cost"]
                return False
            for monster in targets:
                monster.wake_up()
                monster.take_damage(skill["damage"])
                self.log_message(f"Multi-Shot hits {monster.monster_type} for {skill['damage']}!")
                self.pending_animations.append({
                    "type": "player_slash",
                    "world_row": monster.world_row, "world_col": monster.world_col,
                    "damage": skill["damage"],
                })
                if not monster.is_alive():
                    self._handle_monster_death(player, monster, monster.world_row, monster.world_col)
            self.world.remove_dead_monsters()

        elif effect == "trap":
            dist = abs(target_row - player.world_row) + abs(target_col - player.world_col)
            if dist != 1:
                player.action_points += skill["ap_cost"]
                return False
            if not self.world.is_walkable(target_row, target_col):
                player.action_points += skill["ap_cost"]
                return False
            if self.world.get_monster_at(target_row, target_col):
                player.action_points += skill["ap_cost"]
                return False
            self.traps.append({
                "row": target_row, "col": target_col,
                "damage": skill["damage"], "owner": player,
            })
            self.log_message(f"{player.character_type} placed a trap!")

        # Set cooldown
        player.skill_cooldowns[skill_index] = skill["cooldown"]
        return True

    def get_score_summary(self):
        """Get score summary for game over screen."""
        total_gold = sum(p.gold for p in self.players)
        total_kills = sum(p.monsters_killed for p in self.players)
        max_level = max(p.level for p in self.players)
        return {
            "gold": total_gold,
            "kills": total_kills,
            "max_level": max_level,
            "rounds": self.round_number,
        }

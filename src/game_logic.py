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
        """Find an alive player adjacent to monster (dist=1)."""
        for player in self.players:
            if player.is_alive():
                dist = (abs(player.world_row - monster.world_row) +
                        abs(player.world_col - monster.world_col))
                if dist == 1:
                    return player
        return None

    def _find_player_in_territory(self, monster):
        """Find nearest alive player within monster's territory range from home."""
        nearest = None
        nearest_dist = float('inf')
        for player in self.players:
            if player.is_alive():
                # Distance from monster's home to player
                home_dist = (abs(player.world_row - monster.home_row) +
                             abs(player.world_col - monster.home_col))
                if home_dist <= monster.territory_range:
                    monster_dist = (abs(player.world_row - monster.world_row) +
                                   abs(player.world_col - monster.world_col))
                    if monster_dist < nearest_dist:
                        nearest_dist = monster_dist
                        nearest_player = player
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
            if (self.world.is_walkable(new_r, new_c) and
                    not self.world.get_monster_at(new_r, new_c)):
                blocked = any(p.world_row == new_r and p.world_col == new_c
                              for p in self.players)
                if not blocked:
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
            if (self.world.is_walkable(new_r, new_c) and
                    not self.world.get_monster_at(new_r, new_c)):
                blocked = any(p.world_row == new_r and p.world_col == new_c
                              for p in self.players)
                if not blocked:
                    monster.world_row = new_r
                    monster.world_col = new_c
                    self._check_trap(monster, new_r, new_c)
                    return

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
        # Build set of occupied positions (monsters + other players)
        occupied = set()
        for m in self.world.get_alive_monsters():
            occupied.add((m.world_row, m.world_col))
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
        """Get monsters within player's attack range."""
        attackable = []
        for monster in self.world.get_alive_monsters():
            dist = (abs(monster.world_row - player.world_row) +
                    abs(monster.world_col - player.world_col))
            if 1 <= dist <= player.attack_range:
                attackable.append(monster)
        return attackable

    def get_adjacent_monsters(self, player):
        """Get monsters adjacent to player (distance 1 only)."""
        adjacent = []
        for monster in self.world.get_alive_monsters():
            dist = (abs(monster.world_row - player.world_row) +
                    abs(monster.world_col - player.world_col))
            if dist == 1:
                adjacent.append(monster)
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

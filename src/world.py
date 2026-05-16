"""Mini Dungeon - World Map Management"""

from constants import (
    CARD_COLS, CARD_ROWS, TILE_ROAD, TILE_WALL, TILE_DOOR,
    TILE_DOOR_LOCKED, TILE_CHEST, BOSS_GRID_ROWS, BOSS_GRID_COLS
)
from dungeon import DungeonDeck, DungeonCard
from entities import Monster


class WorldMap:
    """Manages the world grid composed of dungeon cards."""

    def __init__(self):
        self.deck = DungeonDeck()
        # Cards placed at (card_row, card_col) positions
        self.cards = {}  # (card_row, card_col) -> DungeonCard
        # World tile grid - dynamically sized
        # world_row = card_row * CARD_ROWS + local_row
        # world_col = card_col * CARD_COLS + local_col
        self.monsters = []
        self.opened_chests = set()  # (world_row, world_col)
        self.opened_doors = set()  # (world_row, world_col)

        # Boss room tracking
        self.boss_room = None  # dict with origin, door_tile, locked, card_positions

        # Place initial card at (0, 0)
        self._place_card(0, 0)

    def _place_card(self, card_row, card_col):
        """Place a new dungeon card at the given card position."""
        if (card_row, card_col) in self.cards:
            return

        card = self.deck.draw_card()
        self.cards[(card_row, card_col)] = card

        # Spawn monsters from the card
        for local_r, local_c, monster_type in card.monsters:
            world_r = card_row * CARD_ROWS + local_r
            world_c = card_col * CARD_COLS + local_c
            self.monsters.append(Monster(monster_type, world_r, world_c))

    def get_tile(self, world_row, world_col):
        """Get the tile type at a world position."""
        card_row = world_row // CARD_ROWS
        card_col = world_col // CARD_COLS
        local_row = world_row % CARD_ROWS
        local_col = world_col % CARD_COLS

        # Handle negative coordinates
        if world_row < 0:
            card_row = -((-world_row - 1) // CARD_ROWS + 1)
            local_row = world_row - card_row * CARD_ROWS
        if world_col < 0:
            card_col = -((-world_col - 1) // CARD_COLS + 1)
            local_col = world_col - card_col * CARD_COLS

        if (card_row, card_col) not in self.cards:
            return None  # Unexplored

        card = self.cards[(card_row, card_col)]

        # Check if door has been opened
        if (world_row, world_col) in self.opened_doors:
            return TILE_ROAD

        # Check if chest has been opened
        if (world_row, world_col) in self.opened_chests:
            return TILE_ROAD

        return card.tiles[local_row][local_col]

    def is_walkable(self, world_row, world_col):
        """Check if a tile is walkable."""
        tile = self.get_tile(world_row, world_col)
        if tile is None:
            return False
        return tile == TILE_ROAD

    def is_door(self, world_row, world_col):
        """Check if tile is a door."""
        tile = self.get_tile(world_row, world_col)
        return tile in (TILE_DOOR, TILE_DOOR_LOCKED)

    def is_locked_door(self, world_row, world_col):
        """Check if tile is a locked door."""
        tile = self.get_tile(world_row, world_col)
        return tile == TILE_DOOR_LOCKED

    def is_chest(self, world_row, world_col):
        """Check if tile is an unopened chest."""
        tile = self.get_tile(world_row, world_col)
        return tile == TILE_CHEST

    def open_door(self, world_row, world_col):
        """Open a door at the given position."""
        self.opened_doors.add((world_row, world_col))

    def open_chest(self, world_row, world_col):
        """Open a chest at the given position."""
        self.opened_chests.add((world_row, world_col))

    def get_monster_at(self, world_row, world_col):
        """Get monster at position, or None. Supports multi-tile monsters."""
        for monster in self.monsters:
            if monster.is_alive() and monster.occupies_tile(world_row, world_col):
                return monster
        return None

    def check_edge_and_expand(self, world_row, world_col):
        """Expand map only when player steps on a connection point at card edge.
        Connection points are the center tile of each edge (always road)."""
        card_row = world_row // CARD_ROWS
        card_col = world_col // CARD_COLS
        local_row = world_row % CARD_ROWS
        local_col = world_col % CARD_COLS

        if world_row < 0:
            card_row = -((-world_row - 1) // CARD_ROWS + 1)
            local_row = world_row - card_row * CARD_ROWS
        if world_col < 0:
            card_col = -((-world_col - 1) // CARD_COLS + 1)
            local_col = world_col - card_col * CARD_COLS

        # Don't expand from boss room sub-cards
        card = self.cards.get((card_row, card_col))
        if card and card.is_boss_sub:
            return

        center_row = CARD_ROWS // 2
        center_col = CARD_COLS // 2

        # Only expand at connection points (center of each edge)
        if local_row == 0 and local_col == center_col:
            self._try_place_card(card_row - 1, card_col)
        if local_row == CARD_ROWS - 1 and local_col == center_col:
            self._try_place_card(card_row + 1, card_col)
        if local_col == 0 and local_row == center_row:
            self._try_place_card(card_row, card_col - 1)
        if local_col == CARD_COLS - 1 and local_row == center_row:
            self._try_place_card(card_row, card_col + 1)

    def _try_place_card(self, card_row, card_col):
        """Place a card if not already placed. May place boss room."""
        if (card_row, card_col) in self.cards:
            return

        # Check if we should place boss room
        if self.deck.should_draw_boss():
            self._try_place_boss_room(card_row, card_col)
        else:
            self._place_card(card_row, card_col)

    def _try_place_boss_room(self, trigger_card_row, trigger_card_col):
        """Place a 3x3 boss room grid anchored at the trigger position."""
        # Determine entry side based on which direction the player is expanding
        # The trigger card is where the boss room connects to the existing map.
        # We need to figure out which side of the 3x3 block faces the source.
        # The trigger card IS part of the boss room (the entry edge).

        # Find which existing card triggered this expansion
        # Check neighbors to find the source card
        entry_side = "top"
        if (trigger_card_row + 1, trigger_card_col) in self.cards:
            entry_side = "top"  # source is below, boss room extends up
        elif (trigger_card_row - 1, trigger_card_col) in self.cards:
            entry_side = "bottom"  # source is above
        elif (trigger_card_row, trigger_card_col + 1) in self.cards:
            entry_side = "left"  # source is to the right
        elif (trigger_card_row, trigger_card_col - 1) in self.cards:
            entry_side = "right"  # source is to the left

        # Calculate the origin (top-left card of 3x3 grid)
        # The trigger card should be the middle of the entry edge
        if entry_side == "top":
            origin_r = trigger_card_row - (BOSS_GRID_ROWS - 1)
            origin_c = trigger_card_col - BOSS_GRID_COLS // 2
        elif entry_side == "bottom":
            origin_r = trigger_card_row
            origin_c = trigger_card_col - BOSS_GRID_COLS // 2
        elif entry_side == "left":
            origin_r = trigger_card_row - BOSS_GRID_ROWS // 2
            origin_c = trigger_card_col - (BOSS_GRID_COLS - 1)
        else:  # right
            origin_r = trigger_card_row - BOSS_GRID_ROWS // 2
            origin_c = trigger_card_col

        # Check if all 9 positions are available
        for gr in range(BOSS_GRID_ROWS):
            for gc in range(BOSS_GRID_COLS):
                pos = (origin_r + gr, origin_c + gc)
                if pos in self.cards:
                    # Can't place boss here, fall back to normal card
                    self._place_card(trigger_card_row, trigger_card_col)
                    return

        # Generate boss room cards
        boss_cards, door_info = self.deck.generate_boss_cards(entry_side)
        door_card_gr, door_card_gc, door_local_r, door_local_c = door_info

        # Place all 9 cards
        card_positions = set()
        for (gr, gc), card in boss_cards.items():
            world_card_r = origin_r + gr
            world_card_c = origin_c + gc
            self.cards[(world_card_r, world_card_c)] = card
            card_positions.add((world_card_r, world_card_c))

            # Spawn monsters
            for local_r, local_c, monster_type in card.monsters:
                world_r = world_card_r * CARD_ROWS + local_r
                world_c = world_card_c * CARD_COLS + local_c
                self.monsters.append(Monster(monster_type, world_r, world_c, elite=True))

        # Calculate door world position
        door_world_r = (origin_r + door_card_gr) * CARD_ROWS + door_local_r
        door_world_c = (origin_c + door_card_gc) * CARD_COLS + door_local_c

        # Store boss room metadata
        self.boss_room = {
            "origin": (origin_r, origin_c),
            "card_positions": card_positions,
            "door_tile": (door_world_r, door_world_c),
            "locked": False,
            "entry_side": entry_side,
        }

    def check_boss_room_entry(self, world_row, world_col):
        """Check if player entered boss room and lock the door.
        Returns True if door was just locked (for message display)."""
        if self.boss_room is None or self.boss_room["locked"]:
            return False

        # Check if the player is inside the boss room (not on the door tile)
        door_r, door_c = self.boss_room["door_tile"]
        if (world_row, world_col) == (door_r, door_c):
            return False  # Still on the door, not inside yet

        # Check if player is on any boss room card
        card_row = world_row // CARD_ROWS
        card_col = world_col // CARD_COLS
        if world_row < 0:
            card_row = -((-world_row - 1) // CARD_ROWS + 1)
        if world_col < 0:
            card_col = -((-world_col - 1) // CARD_COLS + 1)

        if (card_row, card_col) in self.boss_room["card_positions"]:
            # Player is inside the boss room — lock the door!
            self.boss_room["locked"] = True
            # Change door tile to wall (sealed)
            card = self.cards.get((door_r // CARD_ROWS, door_c // CARD_COLS))
            if card:
                local_r = door_r % CARD_ROWS
                local_c = door_c % CARD_COLS
                card.tiles[local_r][local_c] = TILE_WALL
            return True
        return False

    def get_alive_monsters(self):
        """Get list of alive monsters."""
        return [m for m in self.monsters if m.is_alive()]

    def remove_dead_monsters(self):
        """Remove dead monsters from the list."""
        self.monsters = [m for m in self.monsters if m.is_alive()]

    def get_card_bounds(self):
        """Get the world coordinate bounds of all placed cards."""
        if not self.cards:
            return (0, 0, CARD_COLS, CARD_ROWS)

        min_r = min(cr for cr, _ in self.cards) * CARD_ROWS
        max_r = (max(cr for cr, _ in self.cards) + 1) * CARD_ROWS
        min_c = min(cc for _, cc in self.cards) * CARD_COLS
        max_c = (max(cc for _, cc in self.cards) + 1) * CARD_COLS
        return (min_c, min_r, max_c, max_r)

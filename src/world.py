"""Mini Dungeon - World Map Management"""

from constants import (
    CARD_COLS, CARD_ROWS, TILE_ROAD, TILE_WALL, TILE_DOOR,
    TILE_DOOR_LOCKED, TILE_CHEST
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
        """Get monster at position, or None."""
        for monster in self.monsters:
            if (monster.world_row == world_row and
                    monster.world_col == world_col and monster.is_alive()):
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

        center_row = CARD_ROWS // 2  # 3
        center_col = CARD_COLS // 2  # 5

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
        """Place a card if not already placed."""
        if (card_row, card_col) not in self.cards:
            self._place_card(card_row, card_col)

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

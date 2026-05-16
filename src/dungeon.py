"""Mini Dungeon - Dungeon Card Generation"""

import random
from constants import (
    CARD_COLS, CARD_ROWS, TILE_ROAD, TILE_WALL, TILE_DOOR,
    TILE_DOOR_LOCKED, TILE_CHEST, MONSTERS, BOSS_CARD_THRESHOLD
)


class DungeonCard:
    """A 5x7 dungeon card with tiles, monsters, and items."""

    def __init__(self, card_id, is_boss=False):
        self.card_id = card_id
        self.is_boss = is_boss
        self.is_first = (card_id == 1)
        self.tiles = [[TILE_WALL] * CARD_COLS for _ in range(CARD_ROWS)]
        self.monsters = []  # list of (row, col, monster_type)
        self.chests = []  # list of (row, col)
        self._generate()

    def _generate(self):
        """Generate dungeon card layout."""
        if self.is_boss:
            self._generate_boss_room()
        else:
            self._generate_normal()

    def _generate_normal(self):
        """Generate a normal dungeon card with paths, monsters, chests, doors."""
        # Ensure center of each edge is road (connection points)
        # Top edge center: (0, 5)
        # Bottom edge center: (6, 5)
        # Left edge center: (3, 0)
        # Right edge center: (3, 10)

        # Start by carving paths from each edge connection point
        connection_points = [
            (0, CARD_COLS // 2),   # top
            (CARD_ROWS - 1, CARD_COLS // 2),  # bottom
            (CARD_ROWS // 2, 0),   # left
            (CARD_ROWS // 2, CARD_COLS - 1),  # right
        ]

        # Make connection points road
        for r, c in connection_points:
            self.tiles[r][c] = TILE_ROAD

        # Generate paths connecting all connection points through center area
        center_r, center_c = CARD_ROWS // 2, CARD_COLS // 2
        self.tiles[center_r][center_c] = TILE_ROAD

        # Carve paths from each connection to center
        for r, c in connection_points:
            self._carve_path(r, c, center_r, center_c)

        # Add some random rooms/corridors
        num_rooms = random.randint(1, 2)
        for _ in range(num_rooms):
            room_r = random.randint(1, CARD_ROWS - 2)
            room_c = random.randint(1, CARD_COLS - 2)
            room_w = random.randint(2, 3)
            room_h = random.randint(2, 3)
            self._carve_room(room_r, room_c, room_w, room_h)
            # Connect room to center
            self._carve_path(room_r, room_c, center_r, center_c)

        # Add random extra corridors for variety
        for _ in range(random.randint(1, 3)):
            r1 = random.randint(1, CARD_ROWS - 2)
            c1 = random.randint(1, CARD_COLS - 2)
            r2 = random.randint(1, CARD_ROWS - 2)
            c2 = random.randint(1, CARD_COLS - 2)
            self._carve_path(r1, c1, r2, c2)

        # Place doors (on road tiles that are narrow passages)
        self._place_doors()

        # First card has no monsters or chests — safe starting area
        if self.is_first:
            return

        # Place monsters on road tiles
        self._place_monsters()

        # Place chests on road tiles
        self._place_chests()

    def _generate_boss_room(self):
        """Generate the boss room card."""
        # Large open room with boss in center
        for r in range(1, CARD_ROWS - 1):
            for c in range(1, CARD_COLS - 1):
                self.tiles[r][c] = TILE_ROAD

        # Connection points
        self.tiles[0][CARD_COLS // 2] = TILE_ROAD
        self.tiles[CARD_ROWS - 1][CARD_COLS // 2] = TILE_ROAD
        self.tiles[CARD_ROWS // 2][0] = TILE_ROAD
        self.tiles[CARD_ROWS // 2][CARD_COLS - 1] = TILE_ROAD

        # Place boss in center
        self.monsters.append((CARD_ROWS // 2, CARD_COLS // 2, "Boss"))

        # Place some guard monsters
        guards = [(1, 2), (1, 4), (3, 2), (3, 4)]
        for r, c in guards:
            monster_type = random.choice(["Spider", "Skeleton", "Orc", "Wraith"])
            self.monsters.append((r, c, monster_type))

    def _carve_path(self, r1, c1, r2, c2):
        """Carve a path between two points (L-shaped)."""
        r, c = r1, c1
        # Move horizontally first, then vertically (or randomly choose)
        if random.random() < 0.5:
            # Horizontal then vertical
            while c != c2:
                c += 1 if c2 > c else -1
                if 0 <= r < CARD_ROWS and 0 <= c < CARD_COLS:
                    if self.tiles[r][c] == TILE_WALL:
                        self.tiles[r][c] = TILE_ROAD
            while r != r2:
                r += 1 if r2 > r else -1
                if 0 <= r < CARD_ROWS and 0 <= c < CARD_COLS:
                    if self.tiles[r][c] == TILE_WALL:
                        self.tiles[r][c] = TILE_ROAD
        else:
            # Vertical then horizontal
            while r != r2:
                r += 1 if r2 > r else -1
                if 0 <= r < CARD_ROWS and 0 <= c < CARD_COLS:
                    if self.tiles[r][c] == TILE_WALL:
                        self.tiles[r][c] = TILE_ROAD
            while c != c2:
                c += 1 if c2 > c else -1
                if 0 <= r < CARD_ROWS and 0 <= c < CARD_COLS:
                    if self.tiles[r][c] == TILE_WALL:
                        self.tiles[r][c] = TILE_ROAD

    def _carve_room(self, start_r, start_c, width, height):
        """Carve a rectangular room."""
        for r in range(start_r, min(start_r + height, CARD_ROWS - 1)):
            for c in range(start_c, min(start_c + width, CARD_COLS - 1)):
                if 0 < r < CARD_ROWS - 1 and 0 < c < CARD_COLS - 1:
                    self.tiles[r][c] = TILE_ROAD

    def _place_doors(self):
        """Place 0-2 doors on narrow passages."""
        door_candidates = []
        for r in range(1, CARD_ROWS - 1):
            for c in range(1, CARD_COLS - 1):
                if self.tiles[r][c] == TILE_ROAD:
                    # Check if it's a narrow passage (walls on 2 opposite sides)
                    h_walls = (self.tiles[r][c-1] == TILE_WALL and
                               self.tiles[r][c+1] == TILE_WALL)
                    v_walls = (self.tiles[r-1][c] == TILE_WALL and
                               self.tiles[r+1][c] == TILE_WALL)
                    if h_walls or v_walls:
                        door_candidates.append((r, c))

        num_doors = min(random.randint(0, 2), len(door_candidates))
        if door_candidates and num_doors > 0:
            chosen = random.sample(door_candidates, num_doors)
            for r, c in chosen:
                if random.random() < 0.3:
                    self.tiles[r][c] = TILE_DOOR_LOCKED
                else:
                    self.tiles[r][c] = TILE_DOOR

    def _place_monsters(self):
        """Place 1-4 monsters on road tiles."""
        road_tiles = []
        center_r, center_c = CARD_ROWS // 2, CARD_COLS // 2
        for r in range(CARD_ROWS):
            for c in range(CARD_COLS):
                if self.tiles[r][c] == TILE_ROAD:
                    # Don't place on connection points or very center
                    if (r, c) not in [(0, CARD_COLS//2), (CARD_ROWS-1, CARD_COLS//2),
                                      (CARD_ROWS//2, 0), (CARD_ROWS//2, CARD_COLS-1),
                                      (center_r, center_c)]:
                        road_tiles.append((r, c))

        num_monsters = min(random.randint(1, 3), len(road_tiles))
        if road_tiles:
            positions = random.sample(road_tiles, num_monsters)
            for r, c in positions:
                # Weighted selection from all normal monster types
                types =   ["Goblin", "Bat", "Slime", "Spider", "Skeleton", "Orc", "Wraith"]
                weights = [25,       20,    15,      15,       15,         5,     5]
                monster_type = random.choices(types, weights=weights, k=1)[0]
                self.monsters.append((r, c, monster_type))

    def _place_chests(self):
        """Place 0-2 chests on road tiles without monsters."""
        monster_positions = set((r, c) for r, c, _ in self.monsters)
        road_tiles = []
        for r in range(CARD_ROWS):
            for c in range(CARD_COLS):
                if (self.tiles[r][c] == TILE_ROAD and
                        (r, c) not in monster_positions):
                    road_tiles.append((r, c))

        num_chests = min(random.randint(0, 2), len(road_tiles))
        if road_tiles and num_chests > 0:
            positions = random.sample(road_tiles, num_chests)
            for r, c in positions:
                self.tiles[r][c] = TILE_CHEST
                self.chests.append((r, c))


class DungeonDeck:
    """Manages the deck of dungeon cards."""

    def __init__(self):
        self.cards_drawn = 0
        self.boss_drawn = False

    def draw_card(self):
        """Draw the next dungeon card."""
        self.cards_drawn += 1
        if self.cards_drawn > BOSS_CARD_THRESHOLD and not self.boss_drawn:
            self.boss_drawn = True
            return DungeonCard(self.cards_drawn, is_boss=True)
        return DungeonCard(self.cards_drawn)

    def can_draw_boss(self):
        """Check if boss card is available to draw."""
        return self.cards_drawn >= BOSS_CARD_THRESHOLD and not self.boss_drawn

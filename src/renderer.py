"""Mini Dungeon - Renderer (draws the game world and UI)"""

import math
import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, CARD_COLS, CARD_ROWS,
    COLOR_BG, COLOR_ROAD, COLOR_WALL, COLOR_WALL_HATCH, COLOR_DOOR,
    COLOR_DOOR_LOCKED, COLOR_CHEST, COLOR_GRID_LINE, COLOR_INK,
    COLOR_INK_LIGHT, COLOR_UI_BG, COLOR_UI_TEXT, COLOR_UI_HIGHLIGHT,
    COLOR_HEALTH_BAR, COLOR_HEALTH_BG, COLOR_AP_BAR, COLOR_BOSS,
    TILE_ROAD, TILE_WALL, TILE_DOOR, TILE_DOOR_LOCKED, TILE_CHEST,
    STRINGS, HUD_PANEL_HEIGHT, COLOR_PARCHMENT, COLOR_PARCHMENT_DARK,
    COLOR_UI_BUTTON, COLOR_UI_BUTTON_HOVER,
    COLOR_TABLE, COLOR_TABLE_DARK, COLOR_TABLE_LIGHT,
    COLOR_CARD_EDGE, COLOR_CARD_SHADOW,
)


class Camera:
    """Camera for panning the view."""

    def __init__(self):
        self.x = 0
        self.y = 0

    def center_on(self, world_row, world_col, offset_x=0, offset_y=0):
        """Center camera on a world tile, accounting for HUD."""
        visible_height = SCREEN_HEIGHT - HUD_PANEL_HEIGHT
        self.x = world_col * TILE_SIZE - SCREEN_WIDTH // 2 + TILE_SIZE // 2 + offset_x
        self.y = world_row * TILE_SIZE - visible_height // 2 + TILE_SIZE // 2 + offset_y

    def world_to_screen(self, world_row, world_col):
        """Convert world tile coords to screen pixel coords."""
        sx = world_col * TILE_SIZE - self.x
        sy = world_row * TILE_SIZE - self.y
        return (sx, sy)

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen pixel coords to world tile coords."""
        world_col = (screen_x + self.x) // TILE_SIZE
        world_row = (screen_y + self.y) // TILE_SIZE
        return (world_row, world_col)


class Renderer:
    """Handles all game rendering."""

    def __init__(self, screen):
        self.screen = screen
        self.camera = Camera()
        self.frame_count = 0
        self.animations = []  # Active animation effects
        self.font_tiny = pygame.font.Font(None, 14)
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 42)
        self.font_title = pygame.font.Font(None, 72)
        self.font_damage = pygame.font.Font(None, 52)
        # Pre-render wood grain table texture
        self._table_texture = self._generate_table_texture()
        # Pre-render tile texture variants for rich visuals
        self._tile_cache = self._generate_tile_cache()
        # Wall shadow overlay (alpha surface, per-edge)
        self._wall_shadow_cache = self._generate_wall_shadow_cache()
        # Ambient dust particles (screen-space)
        self._dust_particles = self._init_dust_particles(40)
        # Pre-render torch glow surface
        self._torch_glow_surf = self._generate_torch_glow()

    def _generate_table_texture(self):
        """Pre-render a wood grain table surface."""
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill(COLOR_TABLE)
        rng = random.Random(42)  # Deterministic seed
        # Horizontal grain lines
        for y in range(0, SCREEN_HEIGHT, 2):
            intensity = rng.randint(-8, 8)
            r = max(0, min(255, COLOR_TABLE[0] + intensity))
            g = max(0, min(255, COLOR_TABLE[1] + intensity))
            b = max(0, min(255, COLOR_TABLE[2] + intensity))
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        # Darker grain streaks
        for _ in range(20):
            y = rng.randint(0, SCREEN_HEIGHT)
            thickness = rng.randint(1, 3)
            # Slightly wavy line
            points = []
            for x in range(0, SCREEN_WIDTH + 20, 20):
                py = y + rng.randint(-2, 2)
                points.append((x, py))
            if len(points) >= 2:
                pygame.draw.lines(surf, COLOR_TABLE_DARK, False, points, thickness)
        # Lighter grain highlights
        for _ in range(10):
            y = rng.randint(0, SCREEN_HEIGHT)
            points = []
            for x in range(0, SCREEN_WIDTH + 30, 30):
                py = y + rng.randint(-1, 1)
                points.append((x, py))
            if len(points) >= 2:
                pygame.draw.lines(surf, COLOR_TABLE_LIGHT, False, points, 1)
        # Subtle knot spots
        for _ in range(5):
            kx = rng.randint(50, SCREEN_WIDTH - 50)
            ky = rng.randint(50, SCREEN_HEIGHT - 50)
            kr = rng.randint(8, 18)
            pygame.draw.circle(surf, COLOR_TABLE_DARK, (kx, ky), kr, 2)
            pygame.draw.circle(surf, COLOR_TABLE_DARK, (kx, ky), kr // 2, 1)
        return surf

    def _generate_tile_cache(self):
        """Pre-render tile texture variants for rich visuals."""
        TS = TILE_SIZE
        cache = {"floor": [], "wall": [], "door": None, "door_locked": None, "chest": None}
        rng = random.Random(12345)

        # --- Stone floor variants (6) ---
        for v in range(6):
            s = pygame.Surface((TS, TS))
            # Base color with slight variation
            base_r, base_g, base_b = COLOR_ROAD
            br = base_r + rng.randint(-6, 6)
            bg = base_g + rng.randint(-6, 6)
            bb = base_b + rng.randint(-6, 6)
            s.fill((br, bg, bb))
            # Stone slab grid (2x2 or 2x3 pattern)
            slab_h = TS // 2 + rng.randint(-2, 2)
            # Horizontal mortar line
            mortar = (max(0, br - 15), max(0, bg - 15), max(0, bb - 15))
            mortar_hi = (min(255, br + 8), min(255, bg + 8), min(255, bb + 8))
            pygame.draw.line(s, mortar, (0, slab_h), (TS, slab_h), 1)
            pygame.draw.line(s, mortar_hi, (0, slab_h + 1), (TS, slab_h + 1), 1)
            # Vertical mortar lines (staggered)
            off1 = TS // 3 + rng.randint(-3, 3)
            off2 = 2 * TS // 3 + rng.randint(-3, 3)
            pygame.draw.line(s, mortar, (off1, 0), (off1, slab_h), 1)
            pygame.draw.line(s, mortar, (off2, slab_h), (off2, TS), 1)
            # Subtle surface noise (sparse pixels, not every pixel)
            for _ in range(25):
                px = rng.randint(0, TS - 1)
                py = rng.randint(0, TS - 1)
                noise = rng.randint(-10, 10)
                c = (max(0, min(255, br + noise)),
                     max(0, min(255, bg + noise)),
                     max(0, min(255, bb + noise)))
                s.set_at((px, py), c)
            # Cracks (1-2 per variant)
            for _ in range(rng.randint(1, 2)):
                cx = rng.randint(6, TS - 6)
                cy = rng.randint(6, TS - 6)
                crack_color = (max(0, br - 20), max(0, bg - 20), max(0, bb - 20))
                length = rng.randint(8, 18)
                for ci in range(length):
                    dx = rng.choice([-1, 0, 1])
                    dy = rng.choice([0, 1])
                    cx = max(0, min(TS - 1, cx + dx))
                    cy = max(0, min(TS - 1, cy + dy))
                    s.set_at((cx, cy), crack_color)
            # Worn spot (lighter circle)
            if v % 3 == 0:
                wx = rng.randint(10, TS - 10)
                wy = rng.randint(10, TS - 10)
                worn = pygame.Surface((12, 12), pygame.SRCALPHA)
                pygame.draw.circle(worn, (min(255, br + 12), min(255, bg + 12),
                                          min(255, bb + 12), 40), (6, 6), 6)
                s.blit(worn, (wx - 6, wy - 6))
            # Edge highlight (top/left = slightly lighter for depth)
            pygame.draw.line(s, mortar_hi, (0, 0), (TS - 1, 0), 1)
            pygame.draw.line(s, mortar_hi, (0, 0), (0, TS - 1), 1)
            cache["floor"].append(s)

        # --- Brick wall variants (4) ---
        for v in range(4):
            s = pygame.Surface((TS, TS))
            wb_r, wb_g, wb_b = COLOR_WALL
            s.fill((wb_r + rng.randint(-4, 4), wb_g + rng.randint(-4, 4),
                    wb_b + rng.randint(-4, 4)))
            brick_h = 10
            mortar_c = (max(0, wb_r - 10), max(0, wb_g - 10), max(0, wb_b - 10))
            for by in range(0, TS, brick_h):
                # Mortar line
                pygame.draw.line(s, mortar_c, (0, by), (TS, by), 1)
                # Individual bricks with color variation
                stagger = (TS // 3) if (by // brick_h) % 2 == 0 else (2 * TS // 3)
                # Brick tops (highlight)
                hi = (min(255, wb_r + 12), min(255, wb_g + 12), min(255, wb_b + 12))
                pygame.draw.line(s, hi, (0, by + 1), (TS, by + 1), 1)
                # Vertical mortar
                pygame.draw.line(s, mortar_c, (stagger, by), (stagger, by + brick_h), 1)
                # Per-brick color variation
                for bx_start in [0, stagger]:
                    bx_end = stagger if bx_start == 0 else TS
                    bw = bx_end - bx_start
                    if bw > 4:
                        br_v = rng.randint(-6, 6)
                        brick_surf = pygame.Surface((bw - 2, brick_h - 2), pygame.SRCALPHA)
                        brick_surf.fill((max(0, min(255, wb_r + br_v)),
                                         max(0, min(255, wb_g + br_v)),
                                         max(0, min(255, wb_b + br_v)), 60))
                        s.blit(brick_surf, (bx_start + 1, by + 1))
            # Moss/lichen spots
            for _ in range(rng.randint(0, 3)):
                mx = rng.randint(4, TS - 4)
                my = rng.randint(4, TS - 4)
                moss_r = rng.randint(2, 4)
                pygame.draw.circle(s, (35, 50, 30), (mx, my), moss_r)
                pygame.draw.circle(s, (45, 60, 35), (mx, my), moss_r - 1)
            # Chipped brick (dark indent)
            if v % 2 == 0:
                chip_x = rng.randint(8, TS - 8)
                chip_y = rng.randint(4, TS - 4)
                pygame.draw.rect(s, mortar_c,
                                 pygame.Rect(chip_x, chip_y, rng.randint(3, 6),
                                             rng.randint(2, 4)))
            # Dark border
            pygame.draw.rect(s, (max(0, wb_r - 15), max(0, wb_g - 15),
                                  max(0, wb_b - 15)),
                             pygame.Rect(0, 0, TS, TS), 2)
            cache["wall"].append(s)

        # --- Door texture ---
        s = pygame.Surface((TS, TS))
        s.fill(COLOR_ROAD)
        dr = pygame.Rect(6, 3, TS - 12, TS - 6)
        # Wood base
        s.fill(COLOR_DOOR, dr)
        # Wood grain
        for gy in range(dr.top, dr.bottom, 3):
            grain_c = (max(0, COLOR_DOOR[0] + rng.randint(-12, 8)),
                       max(0, COLOR_DOOR[1] + rng.randint(-12, 8)),
                       max(0, COLOR_DOOR[2] + rng.randint(-8, 4)))
            pygame.draw.line(s, grain_c, (dr.left + 1, gy), (dr.right - 1, gy), 1)
        # Plank seams
        for px in [TS // 3, 2 * TS // 3]:
            pygame.draw.line(s, (max(0, COLOR_DOOR[0] - 30), max(0, COLOR_DOOR[1] - 30),
                                  max(0, COLOR_DOOR[2] - 20)),
                             (px, 3), (px, TS - 3), 2)
        # Iron bands
        for band_y in [TS // 4, 3 * TS // 4]:
            pygame.draw.rect(s, (80, 75, 70), pygame.Rect(dr.left, band_y - 2, dr.width, 4))
            pygame.draw.rect(s, (50, 45, 40), pygame.Rect(dr.left, band_y - 2, dr.width, 4), 1)
            # Rivets
            for rx in [dr.left + 6, dr.right - 6]:
                pygame.draw.circle(s, (100, 95, 85), (rx, band_y), 2)
                pygame.draw.circle(s, (60, 55, 50), (rx, band_y), 2, 1)
        # Handle
        pygame.draw.circle(s, (90, 85, 75), (TS - 14, TS // 2), 4)
        pygame.draw.circle(s, (50, 45, 40), (TS - 14, TS // 2), 4, 1)
        pygame.draw.circle(s, (110, 105, 95), (TS - 14, TS // 2), 2)
        # Border
        pygame.draw.rect(s, COLOR_INK, dr, 2)
        cache["door"] = s

        # --- Locked door texture ---
        s2 = s.copy()
        lock_cx = TS // 2
        lock_cy = TS // 2
        # Lock body
        pygame.draw.rect(s2, (70, 65, 55), pygame.Rect(lock_cx - 6, lock_cy - 1, 12, 10))
        pygame.draw.rect(s2, (40, 35, 30), pygame.Rect(lock_cx - 6, lock_cy - 1, 12, 10), 1)
        # Lock shackle
        pygame.draw.arc(s2, (70, 65, 55), pygame.Rect(lock_cx - 4, lock_cy - 8, 8, 10),
                        0, 3.14, 2)
        # Keyhole
        pygame.draw.circle(s2, (30, 25, 20), (lock_cx, lock_cy + 2), 2)
        pygame.draw.line(s2, (30, 25, 20), (lock_cx, lock_cy + 2), (lock_cx, lock_cy + 5), 1)
        cache["door_locked"] = s2

        # --- Chest texture ---
        s = pygame.Surface((TS, TS))
        s.fill(COLOR_ROAD)
        # Shadow under chest
        shadow_surf = pygame.Surface((32, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40), shadow_surf.get_rect())
        s.blit(shadow_surf, (TS // 2 - 16, TS // 2 + 12))
        # Chest body
        cx, cy = TS // 2, TS // 2
        chest_w, chest_h = 30, 22
        body_rect = pygame.Rect(cx - chest_w // 2, cy - chest_h // 2 + 4, chest_w, chest_h)
        # Wood body with grain
        pygame.draw.rect(s, COLOR_CHEST, body_rect)
        for gy in range(body_rect.top, body_rect.bottom, 3):
            gc = (max(0, COLOR_CHEST[0] + rng.randint(-15, 10)),
                  max(0, COLOR_CHEST[1] + rng.randint(-15, 10)),
                  max(0, COLOR_CHEST[2] + rng.randint(-8, 4)))
            pygame.draw.line(s, gc, (body_rect.left + 1, gy), (body_rect.right - 1, gy), 1)
        # Metal bands
        for band_y in [body_rect.top + 4, body_rect.bottom - 5]:
            pygame.draw.line(s, (120, 110, 80), (body_rect.left, band_y),
                             (body_rect.right, band_y), 2)
        pygame.draw.rect(s, COLOR_INK, body_rect, 2)
        # Lid
        lid_rect = pygame.Rect(cx - chest_w // 2, cy - chest_h // 2 - 2, chest_w, 14)
        pygame.draw.arc(s, COLOR_INK, lid_rect, 0, 3.14, 2)
        # Clasp with gem
        pygame.draw.rect(s, (120, 110, 80), pygame.Rect(cx - 4, cy - 2, 8, 8))
        pygame.draw.rect(s, COLOR_INK, pygame.Rect(cx - 4, cy - 2, 8, 8), 1)
        pygame.draw.circle(s, (180, 40, 40), (cx, cy + 2), 2)  # Ruby
        pygame.draw.circle(s, (220, 80, 80), (cx, cy + 1), 1)  # Highlight
        cache["chest"] = s

        return cache

    def _generate_wall_shadow_cache(self):
        """Pre-render shadow overlays for edges adjacent to walls."""
        TS = TILE_SIZE
        shadows = {}
        shadow_depth = 8
        for direction in ["top", "bottom", "left", "right"]:
            s = pygame.Surface((TS, TS), pygame.SRCALPHA)
            for i in range(shadow_depth):
                a = int(50 * (1.0 - i / shadow_depth))
                if direction == "top":
                    pygame.draw.line(s, (0, 0, 0, a), (0, i), (TS, i))
                elif direction == "bottom":
                    pygame.draw.line(s, (0, 0, 0, a), (0, TS - 1 - i), (TS, TS - 1 - i))
                elif direction == "left":
                    pygame.draw.line(s, (0, 0, 0, a), (i, 0), (i, TS))
                elif direction == "right":
                    pygame.draw.line(s, (0, 0, 0, a), (TS - 1 - i, 0), (TS - 1 - i, TS))
            shadows[direction] = s
        # Corner shadow (diagonal)
        for corner in ["tl", "tr", "bl", "br"]:
            s = pygame.Surface((TS, TS), pygame.SRCALPHA)
            for i in range(shadow_depth):
                a = int(35 * (1.0 - i / shadow_depth))
                if corner == "tl":
                    pygame.draw.line(s, (0, 0, 0, a), (0, i), (i, 0))
                elif corner == "tr":
                    pygame.draw.line(s, (0, 0, 0, a), (TS - 1, i), (TS - 1 - i, 0))
                elif corner == "bl":
                    pygame.draw.line(s, (0, 0, 0, a), (0, TS - 1 - i), (i, TS - 1))
                elif corner == "br":
                    pygame.draw.line(s, (0, 0, 0, a), (TS - 1, TS - 1 - i), (TS - 1 - i, TS - 1))
            shadows[corner] = s
        return shadows

    def _init_dust_particles(self, count):
        """Initialize screen-space ambient dust particles."""
        rng = random.Random(999)
        particles = []
        for _ in range(count):
            particles.append({
                "x": rng.uniform(0, SCREEN_WIDTH),
                "y": rng.uniform(0, SCREEN_HEIGHT - HUD_PANEL_HEIGHT),
                "vx": rng.uniform(-0.15, 0.15),
                "vy": rng.uniform(-0.08, 0.05),
                "size": rng.choice([1, 1, 1, 2]),
                "alpha": rng.randint(20, 50),
                "drift_phase": rng.uniform(0, 6.28),
            })
        return particles

    def _generate_torch_glow(self):
        """Pre-render a reusable torch glow surface."""
        glow_radius = TILE_SIZE * 3
        size = glow_radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Warm radial gradient with smooth falloff
        for r in range(glow_radius, 0, -2):
            t = r / glow_radius
            a = int(30 * (1.0 - t * t))  # Quadratic falloff
            warmth = int(40 * (1.0 - t))
            color = (255, 180 + warmth, 80, a)
            pygame.draw.circle(surf, color, (glow_radius, glow_radius), r)
        return surf

    def _draw_table_background(self):
        """Blit the pre-rendered wood grain table."""
        self.screen.blit(self._table_texture, (0, 0))

    def _draw_card_panel(self, rect, radius=8):
        """Draw a card-like panel with cream edge and drop shadow."""
        shadow_offset = 4
        # Drop shadow
        shadow_surf = pygame.Surface(
            (rect.width + shadow_offset * 2, rect.height + shadow_offset * 2),
            pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (30, 25, 20, 100),
                         pygame.Rect(shadow_offset, shadow_offset,
                                     rect.width, rect.height),
                         border_radius=radius)
        self.screen.blit(shadow_surf, (rect.x - shadow_offset // 2,
                                        rect.y - shadow_offset // 2))
        # Card edge (cream border visible around content)
        edge_rect = pygame.Rect(rect.x - 3, rect.y - 3,
                                rect.width + 6, rect.height + 6)
        pygame.draw.rect(self.screen, COLOR_CARD_EDGE, edge_rect,
                         border_radius=radius + 2)
        # Card content area
        pygame.draw.rect(self.screen, COLOR_PARCHMENT, rect,
                         border_radius=radius)

    def _draw_token_shadow(self, cx, cy, radius=12):
        """Draw a board game token shadow (ellipse under piece)."""
        shadow_surf = pygame.Surface((radius * 3, radius * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (20, 15, 10, 80),
                            pygame.Rect(0, 0, radius * 3, radius * 2))
        self.screen.blit(shadow_surf, (cx - radius * 3 // 2, cy + 6))

    def render_game(self, world, players, game_logic, highlights,
                    camera_offset=(0, 0)):
        """Render the full game view."""
        self.frame_count += 1
        # Wood grain table background instead of solid dark
        self._draw_table_background()

        # Center camera on current player with offset
        current_player = game_logic.get_current_player()
        if current_player:
            self.camera.center_on(
                current_player.world_row, current_player.world_col,
                offset_x=camera_offset[0], offset_y=camera_offset[1])

        # Draw tiles
        self._draw_tiles(world)

        # Draw torch glow around players
        self._draw_torch_glow(players)

        # Draw traps
        self._draw_traps(game_logic)

        # Draw highlighted tiles
        self._draw_highlights(highlights)

        # Draw monsters
        self._draw_monsters(world)

        # Draw players
        self._draw_players(players, game_logic)

        # Draw hover effects (path preview + contextual icons)
        self._draw_hover_effects(current_player, highlights)

        # Draw tile interaction effects (chest sparkle, door shimmer)
        self._draw_effects(world)

        # Draw monster-phase vignette
        if game_logic.is_monster_phase:
            self._draw_danger_vignette()

        # Draw HUD panel (covers bottom)
        self._draw_hud(players, game_logic)

        # Draw round banner (top center)
        self._draw_round_banner(game_logic)

        # Draw message log
        self._draw_message_log(game_logic)

        # Consume pending animation events from game logic
        for anim_event in game_logic.pending_animations:
            self._spawn_animation(anim_event)
        game_logic.pending_animations.clear()

        # Draw active animations (on top of everything)
        self._draw_animations()

        # Decorative board game frame around the play area
        self._draw_game_frame()

        # Ambient dust particles (screen-space, drawn last before HUD for atmosphere)
        self._update_and_draw_dust()

    def _draw_tiles(self, world):
        """Draw visible dungeon tiles using pre-rendered textures."""
        # Calculate visible range
        start_col = self.camera.x // TILE_SIZE - 1
        end_col = (self.camera.x + SCREEN_WIDTH) // TILE_SIZE + 1
        start_row = self.camera.y // TILE_SIZE - 1
        end_row = (self.camera.y + SCREEN_HEIGHT) // TILE_SIZE + 1

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = world.get_tile(row, col)
                if tile is None:
                    continue

                sx, sy = self.camera.world_to_screen(row, col)

                if tile == TILE_ROAD:
                    variant = (row * 7 + col * 13) % len(self._tile_cache["floor"])
                    self.screen.blit(self._tile_cache["floor"][variant], (sx, sy))
                elif tile == TILE_WALL:
                    variant = (row * 11 + col * 3) % len(self._tile_cache["wall"])
                    self.screen.blit(self._tile_cache["wall"][variant], (sx, sy))
                elif tile == TILE_DOOR:
                    self.screen.blit(self._tile_cache["door"], (sx, sy))
                elif tile == TILE_DOOR_LOCKED:
                    self.screen.blit(self._tile_cache["door_locked"], (sx, sy))
                elif tile == TILE_CHEST:
                    self.screen.blit(self._tile_cache["chest"], (sx, sy))

                # Subtle grid line
                pygame.draw.rect(self.screen, COLOR_GRID_LINE,
                                 pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE), 1)

        # Wall shadow pass: cast shadows onto adjacent floor tiles
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = world.get_tile(row, col)
                if tile is None or tile == TILE_WALL:
                    continue
                sx, sy = self.camera.world_to_screen(row, col)
                # Check each adjacent direction for walls
                if world.get_tile(row - 1, col) == TILE_WALL:
                    self.screen.blit(self._wall_shadow_cache["top"], (sx, sy))
                if world.get_tile(row + 1, col) == TILE_WALL:
                    self.screen.blit(self._wall_shadow_cache["bottom"], (sx, sy))
                if world.get_tile(row, col - 1) == TILE_WALL:
                    self.screen.blit(self._wall_shadow_cache["left"], (sx, sy))
                if world.get_tile(row, col + 1) == TILE_WALL:
                    self.screen.blit(self._wall_shadow_cache["right"], (sx, sy))
                # Corner shadows (diagonal walls)
                if (world.get_tile(row - 1, col - 1) == TILE_WALL and
                        world.get_tile(row - 1, col) != TILE_WALL and
                        world.get_tile(row, col - 1) != TILE_WALL):
                    self.screen.blit(self._wall_shadow_cache["tl"], (sx, sy))
                if (world.get_tile(row - 1, col + 1) == TILE_WALL and
                        world.get_tile(row - 1, col) != TILE_WALL and
                        world.get_tile(row, col + 1) != TILE_WALL):
                    self.screen.blit(self._wall_shadow_cache["tr"], (sx, sy))

        # Draw card borders (physical card look with shadow + cream edge)
        for (card_row, card_col) in world.cards:
            sx, sy = self.camera.world_to_screen(
                card_row * CARD_ROWS, card_col * CARD_COLS)
            card_w = CARD_COLS * TILE_SIZE
            card_h = CARD_ROWS * TILE_SIZE
            # Drop shadow (offset down-right)
            shadow_surf = pygame.Surface((card_w + 8, card_h + 8), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (20, 15, 10, 100),
                             pygame.Rect(4, 4, card_w, card_h),
                             border_radius=4)
            self.screen.blit(shadow_surf, (sx - 2, sy - 2))
            # Cream card edge (visible border around the card)
            edge_rect = pygame.Rect(sx - 3, sy - 3, card_w + 6, card_h + 6)
            pygame.draw.rect(self.screen, COLOR_CARD_EDGE, edge_rect,
                             border_radius=5)
            # Inner ink border
            border_rect = pygame.Rect(sx, sy, card_w, card_h)
            pygame.draw.rect(self.screen, COLOR_INK, border_rect, 2)
            # Corner decoration dots (like card corner marks)
            for cr, cc in [(sx + 4, sy + 4), (sx + card_w - 5, sy + 4),
                           (sx + 4, sy + card_h - 5), (sx + card_w - 5, sy + card_h - 5)]:
                pygame.draw.circle(self.screen, COLOR_INK, (cr, cc), 2)

    def _draw_highlights(self, highlights):
        """Draw highlighted tiles with color coding by action type."""
        colors = {
            "move": (255, 255, 100, 60),     # Yellow
            "attack": (255, 80, 80, 70),      # Red
            "door": (180, 140, 80, 70),       # Brown
            "chest": (255, 210, 60, 70),      # Gold
            "skill": (160, 60, 220, 50),      # Purple
        }
        border_colors = {
            "move": (255, 255, 100, 150),
            "attack": (255, 80, 80, 180),
            "door": (180, 140, 80, 180),
            "chest": (255, 210, 60, 180),
            "skill": (180, 80, 255, 180),
        }
        for action_type, tiles in highlights.items():
            fill = colors.get(action_type, (255, 255, 100, 60))
            border = border_colors.get(action_type, (255, 255, 100, 150))
            for row, col in tiles:
                sx, sy = self.camera.world_to_screen(row, col)
                highlight_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                highlight_surf.fill(fill)
                self.screen.blit(highlight_surf, (sx, sy))
                pygame.draw.rect(self.screen, border,
                                 pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE), 2)

    def _draw_monsters(self, world):
        """Draw all alive monsters with state-based visuals."""
        for monster in world.get_alive_monsters():
            is_multi = monster.size > 1
            sx, sy = self.camera.world_to_screen(monster.world_row, monster.world_col)

            if is_multi:
                # Multi-tile monster spans size*TILE_SIZE
                tile_span = monster.size * TILE_SIZE
                center_x = sx + tile_span // 2
                center_y = sy + tile_span // 2
                radius = int(tile_span / 3)
            else:
                center_x = sx + TILE_SIZE // 2
                center_y = sy + TILE_SIZE // 2
                radius = TILE_SIZE // 3

            is_sleeping = monster.state == "sleeping"
            is_returning = monster.state == "returning"

            # Determine draw target surface and alpha
            if is_multi:
                tile_span = monster.size * TILE_SIZE
                if is_sleeping:
                    surf = pygame.Surface((tile_span, tile_span), pygame.SRCALPHA)
                    surf.set_alpha(140)
                    lcx, lcy = tile_span // 2, tile_span // 2
                elif is_returning:
                    surf = pygame.Surface((tile_span, tile_span), pygame.SRCALPHA)
                    surf.set_alpha(180)
                    lcx, lcy = tile_span // 2, tile_span // 2
                else:
                    surf = self.screen
                    lcx, lcy = center_x, center_y
            elif is_sleeping:
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                surf.set_alpha(140)
                lcx, lcy = TILE_SIZE // 2, TILE_SIZE // 2
            elif is_returning:
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                surf.set_alpha(180)
                lcx, lcy = TILE_SIZE // 2, TILE_SIZE // 2
            else:
                surf = self.screen
                lcx, lcy = center_x, center_y

            # Board game token shadow (only when drawing directly to screen)
            if not is_sleeping and not is_returning:
                shadow_r = radius + 4 if not is_multi else radius
                self._draw_token_shadow(center_x, center_y, shadow_r)

            # Dispatch to per-type drawing method
            draw_fn = {
                "Goblin": self._draw_goblin,
                "Skeleton": self._draw_skeleton,
                "Orc": self._draw_orc,
                "Boss": self._draw_boss,
                "Bat": self._draw_bat,
                "Slime": self._draw_slime,
                "Spider": self._draw_spider,
                "Wraith": self._draw_wraith,
            }.get(monster.monster_type, self._draw_generic_monster)
            draw_fn(surf, lcx, lcy, radius, monster, is_sleeping)

            # Blit off-screen surfaces
            if is_sleeping or is_returning:
                self.screen.blit(surf, (sx, sy))

            # Sleeping "zzz" bobbing text
            if is_sleeping:
                bob = math.sin(self.frame_count * 0.05) * 3
                zzz = self.font_small.render("zzz", True, COLOR_INK_LIGHT)
                self.screen.blit(zzz, (center_x - zzz.get_width() // 2,
                                       sy - 10 + int(bob)))
                continue  # No health bar for sleeping monsters

            # Chasing exclamation mark
            if monster.state == "chasing":
                ex = self.font_medium.render("!", True, (220, 40, 40))
                self.screen.blit(ex, (center_x + radius + 2,
                                      center_y - radius - 4))

            # Returning: arrow toward home
            if is_returning:
                dr = monster.home_row - monster.world_row
                dc = monster.home_col - monster.world_col
                if dr != 0 or dc != 0:
                    length = math.sqrt(dr * dr + dc * dc)
                    ndx = dc / length * 8
                    ndy = dr / length * 8
                    ax, ay = center_x + int(ndx), center_y + int(ndy)
                    pygame.draw.line(self.screen, COLOR_INK_LIGHT,
                                     (center_x, center_y), (ax, ay), 2)
                    pygame.draw.circle(self.screen, COLOR_INK_LIGHT, (ax, ay), 2)

            # Health bar (gradient fill with depth)
            if is_multi:
                tile_span = monster.size * TILE_SIZE
                bar_w = tile_span - 10
                bar_h = 7
                bar_x = sx + 5
                bar_y = sy + 1
            else:
                bar_w = TILE_SIZE - 10
                bar_h = 6
                bar_x = sx + 5
                bar_y = sy + 1
            # Dark shadow
            pygame.draw.rect(self.screen, (15, 12, 10),
                             pygame.Rect(bar_x + 1, bar_y + 1, bar_w, bar_h))
            # Background
            pygame.draw.rect(self.screen, COLOR_HEALTH_BG,
                             pygame.Rect(bar_x, bar_y, bar_w, bar_h))
            # Gradient health fill (dark red to bright red)
            health_w = int(bar_w * monster.health / monster.max_health)
            if health_w > 0:
                for i in range(bar_h):
                    t = i / bar_h
                    r = int(140 + 60 * (1.0 - t * 0.5))
                    g = int(30 + 20 * (1.0 - t))
                    b = int(30 + 15 * (1.0 - t))
                    pygame.draw.line(self.screen, (r, g, b),
                                     (bar_x, bar_y + i), (bar_x + health_w, bar_y + i))
                # Inner highlight
                pygame.draw.line(self.screen, (220, 80, 80),
                                 (bar_x + 1, bar_y + 1), (bar_x + health_w - 1, bar_y + 1), 1)
            # Border
            pygame.draw.rect(self.screen, COLOR_INK,
                             pygame.Rect(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)
            # HP text on bar for awake monsters
            hp_str = f"{monster.health}/{monster.max_health}"
            hp_surf = self.font_tiny.render(hp_str, True, (255, 255, 255))
            hp_x = bar_x + bar_w // 2 - hp_surf.get_width() // 2
            hp_y = bar_y + bar_h // 2 - hp_surf.get_height() // 2
            self.screen.blit(hp_surf, (hp_x, hp_y))

            # Damage flash overlay
            if monster.damage_flash > 0:
                if is_multi:
                    tile_span = monster.size * TILE_SIZE
                    flash_surf = pygame.Surface((tile_span, tile_span), pygame.SRCALPHA)
                else:
                    flash_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                flash_alpha = min(180, monster.damage_flash * 18)
                flash_surf.fill((255, 255, 255, flash_alpha))
                self.screen.blit(flash_surf, (sx, sy))
                monster.damage_flash -= 1

    # -- Per-monster drawing methods --

    def _draw_sleeping_eyes(self, surf, lcx, lcy):
        """Draw closed eyes (horizontal lines) for sleeping monsters."""
        pygame.draw.line(surf, COLOR_INK, (lcx - 6, lcy - 2), (lcx - 2, lcy - 2), 2)
        pygame.draw.line(surf, COLOR_INK, (lcx + 2, lcy - 2), (lcx + 6, lcy - 2), 2)

    def _draw_goblin(self, surf, lcx, lcy, radius, monster, is_sleeping):
        """Small hunched humanoid with pointy ears."""
        # Oval body (squished)
        body_rect = pygame.Rect(lcx - radius, lcy - radius + 3,
                                radius * 2, int(radius * 1.6))
        pygame.draw.ellipse(surf, monster.color, body_rect)
        pygame.draw.ellipse(surf, COLOR_INK, body_rect, 2)
        # Pointy ears
        ear_y = lcy - radius + 3
        pygame.draw.polygon(surf, monster.color,
                            [(lcx - radius + 2, ear_y + 4),
                             (lcx - radius - 3, ear_y - 8),
                             (lcx - radius + 8, ear_y + 2)])
        pygame.draw.polygon(surf, COLOR_INK,
                            [(lcx - radius + 2, ear_y + 4),
                             (lcx - radius - 3, ear_y - 8),
                             (lcx - radius + 8, ear_y + 2)], 1)
        pygame.draw.polygon(surf, monster.color,
                            [(lcx + radius - 2, ear_y + 4),
                             (lcx + radius + 3, ear_y - 8),
                             (lcx + radius - 8, ear_y + 2)])
        pygame.draw.polygon(surf, COLOR_INK,
                            [(lcx + radius - 2, ear_y + 4),
                             (lcx + radius + 3, ear_y - 8),
                             (lcx + radius - 8, ear_y + 2)], 1)
        if is_sleeping:
            self._draw_sleeping_eyes(surf, lcx, lcy)
        else:
            # Beady dot eyes
            pygame.draw.circle(surf, COLOR_INK, (lcx - 4, lcy - 1), 2)
            pygame.draw.circle(surf, COLOR_INK, (lcx + 4, lcy - 1), 2)
            # Wide grin with fangs
            pygame.draw.line(surf, COLOR_INK, (lcx - 5, lcy + 5), (lcx + 5, lcy + 5), 1)
            pygame.draw.line(surf, COLOR_INK, (lcx - 3, lcy + 5), (lcx - 3, lcy + 7), 1)
            pygame.draw.line(surf, COLOR_INK, (lcx + 3, lcy + 5), (lcx + 3, lcy + 7), 1)

    def _draw_skeleton(self, surf, lcx, lcy, radius, monster, is_sleeping):
        """Skull shape with ribcage."""
        # Circle head
        pygame.draw.circle(surf, monster.color, (lcx, lcy - 2), radius - 2)
        pygame.draw.circle(surf, COLOR_INK, (lcx, lcy - 2), radius - 2, 2)
        if is_sleeping:
            self._draw_sleeping_eyes(surf, lcx, lcy - 2)
        else:
            # Dark hollow eye sockets
            pygame.draw.circle(surf, (20, 15, 10), (lcx - 5, lcy - 5), 4)
            pygame.draw.circle(surf, (20, 15, 10), (lcx + 5, lcy - 5), 4)
            # Nose: inverted V
            pygame.draw.line(surf, COLOR_INK, (lcx - 2, lcy), (lcx, lcy - 3), 1)
            pygame.draw.line(surf, COLOR_INK, (lcx + 2, lcy), (lcx, lcy - 3), 1)
            # Teeth: horizontal jaw with vertical lines
            jaw_y = lcy + 3
            pygame.draw.line(surf, COLOR_INK, (lcx - 6, jaw_y), (lcx + 6, jaw_y), 1)
            for tx in range(-5, 6, 3):
                pygame.draw.line(surf, COLOR_INK, (lcx + tx, jaw_y - 1),
                                 (lcx + tx, jaw_y + 2), 1)
        # Ribcage lines below head
        for i in range(3):
            ry = lcy + radius + i * 3
            hw = 6 - i
            pygame.draw.line(surf, COLOR_INK, (lcx - hw, ry), (lcx + hw, ry), 1)

    def _draw_orc(self, surf, lcx, lcy, radius, monster, is_sleeping):
        """Beefy humanoid with tusks."""
        big_r = radius + 2
        # Large body
        pygame.draw.circle(surf, monster.color, (lcx, lcy + 2), big_r)
        pygame.draw.circle(surf, COLOR_INK, (lcx, lcy + 2), big_r, 2)
        # Small head on top
        head_y = lcy - radius + 2
        pygame.draw.circle(surf, monster.color, (lcx, head_y), radius // 2 + 1)
        pygame.draw.circle(surf, COLOR_INK, (lcx, head_y), radius // 2 + 1, 2)
        if is_sleeping:
            self._draw_sleeping_eyes(surf, lcx, head_y)
        else:
            # Angry V-brow
            pygame.draw.line(surf, COLOR_INK, (lcx - 6, head_y - 4),
                             (lcx - 2, head_y - 2), 2)
            pygame.draw.line(surf, COLOR_INK, (lcx + 6, head_y - 4),
                             (lcx + 2, head_y - 2), 2)
            # Eyes
            pygame.draw.circle(surf, COLOR_INK, (lcx - 4, head_y), 2)
            pygame.draw.circle(surf, COLOR_INK, (lcx + 4, head_y), 2)
        # Tusks from jaw
        tusk_y = head_y + radius // 2
        pygame.draw.line(surf, (240, 230, 210), (lcx - 4, tusk_y),
                         (lcx - 5, tusk_y - 5), 2)
        pygame.draw.line(surf, (240, 230, 210), (lcx + 4, tusk_y),
                         (lcx + 5, tusk_y - 5), 2)

    def _draw_boss(self, surf, lcx, lcy, radius, monster, is_sleeping):
        """Imposing 2x2 boss with prominent crown, horns, and glowing eyes."""
        big_r = radius
        # Dark aura circle behind
        pygame.draw.circle(surf, (60, 10, 60), (lcx, lcy), big_r + 4)
        # Body
        pygame.draw.circle(surf, monster.color, (lcx, lcy), big_r)
        pygame.draw.circle(surf, COLOR_INK, (lcx, lcy), big_r, 3)

        # Armor lines on body
        for i in range(-2, 3):
            y = lcy + i * 8
            pygame.draw.line(surf, (120, 20, 120),
                             (lcx - big_r // 2, y), (lcx + big_r // 2, y), 1)

        # Crown: golden band with 5 points
        crown_base = lcy - big_r - 2
        crown_w = big_r + 6
        # Crown base band
        pygame.draw.rect(surf, (255, 215, 0),
                         pygame.Rect(lcx - crown_w // 2, crown_base, crown_w, 6))
        pygame.draw.rect(surf, COLOR_INK,
                         pygame.Rect(lcx - crown_w // 2, crown_base, crown_w, 6), 1)
        # Crown points (5 tall spikes)
        for i in range(5):
            px = lcx - crown_w // 2 + int(crown_w * i / 4)
            h = 14 if i % 2 == 0 else 10
            pygame.draw.polygon(surf, (255, 215, 0),
                                [(px - 4, crown_base),
                                 (px, crown_base - h),
                                 (px + 4, crown_base)])
            pygame.draw.polygon(surf, COLOR_INK,
                                [(px - 4, crown_base),
                                 (px, crown_base - h),
                                 (px + 4, crown_base)], 1)
            # Jewel on tall points
            if i % 2 == 0:
                pygame.draw.circle(surf, (220, 30, 30), (px, crown_base - h + 4), 2)

        if is_sleeping:
            self._draw_sleeping_eyes(surf, lcx, lcy)
        else:
            # Glowing red eyes
            for ex in [-10, 10]:
                pygame.draw.circle(surf, (255, 60, 60), (lcx + ex, lcy - 6), 5)
                pygame.draw.circle(surf, (255, 200, 200), (lcx + ex, lcy - 6), 2)
                pygame.draw.circle(surf, COLOR_INK, (lcx + ex, lcy - 6), 5, 1)
            # Fangs
            for fx in [-7, 7]:
                pygame.draw.line(surf, (240, 230, 210),
                                 (lcx + fx, lcy + 8), (lcx + fx + (1 if fx > 0 else -1), lcy + 16), 3)
            # Mouth
            pygame.draw.arc(surf, COLOR_INK,
                            pygame.Rect(lcx - 12, lcy + 2, 24, 14), 3.5, 6.0, 2)

    def _draw_bat(self, surf, lcx, lcy, radius, monster, is_sleeping):
        """Wings spread bat."""
        body_r = radius - 4
        # Small body
        pygame.draw.circle(surf, monster.color, (lcx, lcy), body_r)
        pygame.draw.circle(surf, COLOR_INK, (lcx, lcy), body_r, 2)
        # Tiny pointed ear triangles
        pygame.draw.polygon(surf, monster.color,
                            [(lcx - 3, lcy - body_r),
                             (lcx - 6, lcy - body_r - 6),
                             (lcx, lcy - body_r)])
        pygame.draw.polygon(surf, COLOR_INK,
                            [(lcx - 3, lcy - body_r),
                             (lcx - 6, lcy - body_r - 6),
                             (lcx, lcy - body_r)], 1)
        pygame.draw.polygon(surf, monster.color,
                            [(lcx + 3, lcy - body_r),
                             (lcx + 6, lcy - body_r - 6),
                             (lcx, lcy - body_r)])
        pygame.draw.polygon(surf, COLOR_INK,
                            [(lcx + 3, lcy - body_r),
                             (lcx + 6, lcy - body_r - 6),
                             (lcx, lcy - body_r)], 1)
        # Left wing (scalloped polygon)
        wing_pts_l = [(lcx - body_r, lcy - 2),
                      (lcx - radius - 6, lcy - 8),
                      (lcx - radius - 4, lcy + 2),
                      (lcx - radius - 1, lcy + 5),
                      (lcx - body_r, lcy + 3)]
        pygame.draw.polygon(surf, monster.color, wing_pts_l)
        pygame.draw.lines(surf, COLOR_INK, True, wing_pts_l, 1)
        # Right wing
        wing_pts_r = [(lcx + body_r, lcy - 2),
                      (lcx + radius + 6, lcy - 8),
                      (lcx + radius + 4, lcy + 2),
                      (lcx + radius + 1, lcy + 5),
                      (lcx + body_r, lcy + 3)]
        pygame.draw.polygon(surf, monster.color, wing_pts_r)
        pygame.draw.lines(surf, COLOR_INK, True, wing_pts_r, 1)
        if is_sleeping:
            self._draw_sleeping_eyes(surf, lcx, lcy)
        else:
            # Two small red dot eyes
            pygame.draw.circle(surf, (200, 40, 40), (lcx - 3, lcy - 1), 2)
            pygame.draw.circle(surf, (200, 40, 40), (lcx + 3, lcy - 1), 2)

    def _draw_slime(self, surf, lcx, lcy, radius, monster, is_sleeping):
        """Blobby slime creature."""
        # Blob body: wide ellipse
        blob_rect = pygame.Rect(lcx - radius - 2, lcy - radius // 2,
                                (radius + 2) * 2, radius + 4)
        # Lighter shade layer for transparency feel
        lighter = (min(255, monster.color[0] + 40),
                   min(255, monster.color[1] + 40),
                   min(255, monster.color[2] + 40))
        offset_rect = pygame.Rect(blob_rect.x + 2, blob_rect.y + 1,
                                  blob_rect.width - 2, blob_rect.height - 1)
        pygame.draw.ellipse(surf, lighter, offset_rect)
        # Main body
        pygame.draw.ellipse(surf, monster.color, blob_rect)
        pygame.draw.ellipse(surf, COLOR_INK, blob_rect, 2)
        # Bubbles on surface
        pygame.draw.circle(surf, lighter, (lcx - 5, lcy - 2), 3)
        pygame.draw.circle(surf, lighter, (lcx + 6, lcy + 1), 2)
        pygame.draw.circle(surf, lighter, (lcx + 1, lcy - 4), 2)
        if is_sleeping:
            self._draw_sleeping_eyes(surf, lcx, lcy)
        else:
            # Simple happy face
            pygame.draw.circle(surf, COLOR_INK, (lcx - 4, lcy - 1), 2)
            pygame.draw.circle(surf, COLOR_INK, (lcx + 4, lcy - 1), 2)
            # Curved smile arc
            smile_rect = pygame.Rect(lcx - 4, lcy + 1, 8, 6)
            pygame.draw.arc(surf, COLOR_INK, smile_rect, 3.4, 6.0, 1)

    def _draw_spider(self, surf, lcx, lcy, radius, monster, is_sleeping):
        """8-legged spider with abdomen."""
        body_rx, body_ry = radius // 2 + 1, radius // 2
        abd_rx, abd_ry = radius // 2 + 3, radius // 2 + 2
        # Abdomen (behind/below)
        abd_rect = pygame.Rect(lcx - abd_rx, lcy + 1, abd_rx * 2, abd_ry * 2)
        pygame.draw.ellipse(surf, monster.color, abd_rect)
        pygame.draw.ellipse(surf, COLOR_INK, abd_rect, 2)
        # Body (front/top)
        body_rect = pygame.Rect(lcx - body_rx, lcy - body_ry - 2,
                                body_rx * 2, body_ry * 2)
        pygame.draw.ellipse(surf, monster.color, body_rect)
        pygame.draw.ellipse(surf, COLOR_INK, body_rect, 2)
        # 8 legs: 4 per side with joints
        for side in [-1, 1]:
            for i, angle_off in enumerate([-6, -2, 2, 6]):
                bx = lcx + side * body_rx
                by = lcy - 3 + angle_off
                jx = bx + side * 7
                jy = by - 4 + i * 2
                ex = jx + side * 4
                ey = jy + 6
                pygame.draw.line(surf, COLOR_INK, (bx, by), (jx, jy), 1)
                pygame.draw.line(surf, COLOR_INK, (jx, jy), (ex, ey), 1)
        if is_sleeping:
            self._draw_sleeping_eyes(surf, lcx, lcy - 3)
        else:
            # Cluster of 4 small eyes
            for dx, dy in [(-3, -5), (-1, -6), (1, -6), (3, -5)]:
                pygame.draw.circle(surf, COLOR_INK, (lcx + dx, lcy + dy), 1)
            # Fangs
            pygame.draw.line(surf, COLOR_INK, (lcx - 2, lcy), (lcx - 3, lcy + 4), 1)
            pygame.draw.line(surf, COLOR_INK, (lcx + 2, lcy), (lcx + 3, lcy + 4), 1)

    def _draw_wraith(self, surf, lcx, lcy, radius, monster, is_sleeping):
        """Ghostly floating wraith with hood."""
        # Hooded cloak: trapezoid top to wavy bottom
        top_w = radius - 2
        bot_w = radius + 4
        top_y = lcy - radius
        bot_y = lcy + radius
        # Wavy bottom edge points
        wave_pts = []
        for i in range(5):
            wx = lcx - bot_w + i * (bot_w * 2 // 4)
            wy = bot_y + (3 if i % 2 == 0 else -2)
            wave_pts.append((wx, wy))
        cloak_pts = [(lcx - top_w, top_y), (lcx + top_w, top_y),
                     (lcx + bot_w, bot_y)] + list(reversed(wave_pts))[:3] + \
                    [(lcx - bot_w, bot_y)]
        # Draw cloak with slight transparency via alpha surface
        cloak_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        # Offset points if drawing on sub-surface
        if surf != self.screen:
            pygame.draw.polygon(cloak_surf, (*monster.color, 200), cloak_pts)
            pygame.draw.polygon(cloak_surf, (*COLOR_INK, 200), cloak_pts, 2)
            surf.blit(cloak_surf, (0, 0))
        else:
            pygame.draw.polygon(surf, monster.color, cloak_pts)
            pygame.draw.polygon(surf, COLOR_INK, cloak_pts, 2)
        # Hood arc
        hood_rect = pygame.Rect(lcx - top_w - 2, top_y - 4, (top_w + 2) * 2, 12)
        pygame.draw.arc(surf, COLOR_INK, hood_rect, 0.3, 2.8, 2)
        if is_sleeping:
            self._draw_sleeping_eyes(surf, lcx, lcy - 2)
        else:
            # Glowing eyes inside hood
            glow = (min(255, monster.color[0] + 80),
                    min(255, monster.color[1] + 80),
                    min(255, monster.color[2] + 80))
            pygame.draw.circle(surf, glow, (lcx - 5, lcy - 4), 3)
            pygame.draw.circle(surf, glow, (lcx + 5, lcy - 4), 3)

    def _draw_generic_monster(self, surf, lcx, lcy, radius, monster, is_sleeping):
        """Fallback: simple circle with letter (for unknown types)."""
        pygame.draw.circle(surf, monster.color, (lcx, lcy), radius)
        pygame.draw.circle(surf, COLOR_INK, (lcx, lcy), radius, 2)
        if is_sleeping:
            self._draw_sleeping_eyes(surf, lcx, lcy)
        else:
            pygame.draw.circle(surf, COLOR_INK, (lcx - 4, lcy - 2), 2)
            pygame.draw.circle(surf, COLOR_INK, (lcx + 4, lcy - 2), 2)
        letter = self.font_small.render(monster.monster_type[0], True, (255, 255, 255))
        surf.blit(letter, (lcx - letter.get_width() // 2, lcy + 6))

    def _draw_players(self, players, game_logic):
        """Draw all players as colored pawns with damage flash and turn indicator."""
        current_player = game_logic.get_current_player()
        for player in players:
            if not player.is_alive():
                continue
            sx, sy = self.camera.world_to_screen(player.world_row, player.world_col)
            center_x = sx + TILE_SIZE // 2
            center_y = sy + TILE_SIZE // 2

            # Board game token shadow
            self._draw_token_shadow(center_x, center_y, 12)

            # Current-turn golden pulsing ring
            if (player is current_player and not game_logic.is_monster_phase):
                pulse_alpha = int(150 + 50 * math.sin(self.frame_count * 0.08))
                ring_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (255, 200, 80, pulse_alpha),
                                   (TILE_SIZE // 2, TILE_SIZE // 2), 22, 3)
                self.screen.blit(ring_surf, (sx, sy))

            # Pawn shape: circle head + triangular body
            body_points = [
                (center_x, center_y - 10),
                (center_x - 10, center_y + 12),
                (center_x + 10, center_y + 12),
            ]
            pygame.draw.polygon(self.screen, player.color, body_points)
            pygame.draw.polygon(self.screen, COLOR_INK, body_points, 2)
            # Head
            pygame.draw.circle(self.screen, player.color, (center_x, center_y - 12), 7)
            pygame.draw.circle(self.screen, COLOR_INK, (center_x, center_y - 12), 7, 2)
            # Base
            pygame.draw.ellipse(self.screen, player.color,
                                pygame.Rect(center_x - 11, center_y + 10, 22, 8))
            pygame.draw.ellipse(self.screen, COLOR_INK,
                                pygame.Rect(center_x - 11, center_y + 10, 22, 8), 2)

            # Player number on body
            num_text = self.font_small.render(
                str(player.player_id + 1), True, (255, 255, 255))
            self.screen.blit(num_text, (center_x - num_text.get_width() // 2,
                                        center_y - 2))

            # Health bar above (gradient fill with depth)
            bar_w = TILE_SIZE - 10
            bar_h = 6
            bar_x = sx + 5
            bar_y = sy + 1
            # Dark shadow behind bar
            pygame.draw.rect(self.screen, (15, 12, 10),
                             pygame.Rect(bar_x + 1, bar_y + 1, bar_w, bar_h))
            # Background
            pygame.draw.rect(self.screen, COLOR_HEALTH_BG,
                             pygame.Rect(bar_x, bar_y, bar_w, bar_h))
            # Gradient health fill
            health_w = int(bar_w * player.health / player.max_health)
            if health_w > 0:
                for i in range(bar_h):
                    t = i / bar_h
                    r = int(60 + 120 * (1.0 - t * 0.6))
                    g = int(160 + 40 * (1.0 - t))
                    b = int(60 + 20 * (1.0 - t))
                    pygame.draw.line(self.screen, (r, g, b),
                                     (bar_x, bar_y + i), (bar_x + health_w, bar_y + i))
                # Inner highlight line
                pygame.draw.line(self.screen, (140, 220, 140),
                                 (bar_x + 1, bar_y + 1), (bar_x + health_w - 1, bar_y + 1), 1)
            # Border
            pygame.draw.rect(self.screen, COLOR_INK,
                             pygame.Rect(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)
            # HP text on bar
            hp_str = f"{player.health}/{player.max_health}"
            hp_surf = self.font_tiny.render(hp_str, True, (255, 255, 255))
            hp_x = bar_x + bar_w // 2 - hp_surf.get_width() // 2
            hp_y = bar_y + bar_h // 2 - hp_surf.get_height() // 2
            self.screen.blit(hp_surf, (hp_x, hp_y))

            # Damage flash overlay
            if player.damage_flash > 0:
                flash_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                flash_alpha = min(180, player.damage_flash * 18)
                flash_surf.fill((255, 255, 255, flash_alpha))
                self.screen.blit(flash_surf, (sx, sy))
                player.damage_flash -= 1

    def _draw_effects(self, world):
        """Draw tile interaction animations (chest sparkle, door shimmer)."""
        start_col = self.camera.x // TILE_SIZE - 1
        end_col = (self.camera.x + SCREEN_WIDTH) // TILE_SIZE + 1
        start_row = self.camera.y // TILE_SIZE - 1
        end_row = (self.camera.y + SCREEN_HEIGHT) // TILE_SIZE + 1

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = world.get_tile(row, col)
                if tile is None:
                    continue
                sx, sy = self.camera.world_to_screen(row, col)
                cx = sx + TILE_SIZE // 2
                cy = sy + TILE_SIZE // 2

                # Chest sparkle (unopened chests only)
                if tile == TILE_CHEST and (row, col) not in world.opened_chests:
                    t = self.frame_count * 0.06
                    sparkle_alpha = int(120 + 80 * math.sin(t))
                    sparkle_len = int(3 + 2 * math.sin(t))
                    spark_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    sc = TILE_SIZE // 2
                    color = (255, 220, 80, sparkle_alpha)
                    pygame.draw.line(spark_surf, color,
                                     (sc, sc - sparkle_len), (sc, sc + sparkle_len), 1)
                    pygame.draw.line(spark_surf, color,
                                     (sc - sparkle_len, sc), (sc + sparkle_len, sc), 1)
                    self.screen.blit(spark_surf, (sx, sy))

                # Door shimmer (locked doors)
                if tile == TILE_DOOR_LOCKED:
                    t = self.frame_count * 0.04
                    glow_alpha = int(40 + 30 * math.sin(t))
                    glow_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (255, 200, 100, glow_alpha),
                                       (TILE_SIZE // 2, TILE_SIZE // 2), 10)
                    self.screen.blit(glow_surf, (sx, sy))

    def _draw_danger_vignette(self):
        """Draw red vignette around screen edges during monster phase."""
        edge = 60
        alpha = int(40 + 20 * math.sin(self.frame_count * 0.05))
        # Top
        s = pygame.Surface((SCREEN_WIDTH, edge), pygame.SRCALPHA)
        for i in range(edge):
            a = alpha * (edge - i) // edge
            pygame.draw.line(s, (180, 30, 30, a), (0, i), (SCREEN_WIDTH, i))
        self.screen.blit(s, (0, 0))
        # Bottom (above HUD)
        bot_y = SCREEN_HEIGHT - HUD_PANEL_HEIGHT - edge
        s2 = pygame.Surface((SCREEN_WIDTH, edge), pygame.SRCALPHA)
        for i in range(edge):
            a = alpha * i // edge
            pygame.draw.line(s2, (180, 30, 30, a), (0, i), (SCREEN_WIDTH, i))
        self.screen.blit(s2, (0, bot_y))
        # Left
        s3 = pygame.Surface((edge, SCREEN_HEIGHT - HUD_PANEL_HEIGHT), pygame.SRCALPHA)
        for i in range(edge):
            a = alpha * (edge - i) // edge
            pygame.draw.line(s3, (180, 30, 30, a), (i, 0), (i, SCREEN_HEIGHT - HUD_PANEL_HEIGHT))
        self.screen.blit(s3, (0, 0))
        # Right
        s4 = pygame.Surface((edge, SCREEN_HEIGHT - HUD_PANEL_HEIGHT), pygame.SRCALPHA)
        for i in range(edge):
            a = alpha * i // edge
            pygame.draw.line(s4, (180, 30, 30, a), (i, 0), (i, SCREEN_HEIGHT - HUD_PANEL_HEIGHT))
        self.screen.blit(s4, (SCREEN_WIDTH - edge, 0))

    def _draw_game_frame(self):
        """Draw a decorative board game frame around the play area."""
        frame_w = 4
        play_h = SCREEN_HEIGHT - HUD_PANEL_HEIGHT
        # Outer frame (dark wood)
        pygame.draw.rect(self.screen, (50, 35, 22),
                         pygame.Rect(0, 0, SCREEN_WIDTH, play_h), frame_w + 2)
        # Inner frame (lighter wood)
        pygame.draw.rect(self.screen, (80, 60, 38),
                         pygame.Rect(frame_w, frame_w,
                                     SCREEN_WIDTH - frame_w * 2,
                                     play_h - frame_w * 2), 2)
        # Corner ornaments (small circles)
        ornament_r = 6
        for x, y in [(ornament_r + 2, ornament_r + 2),
                      (SCREEN_WIDTH - ornament_r - 2, ornament_r + 2),
                      (ornament_r + 2, play_h - ornament_r - 2),
                      (SCREEN_WIDTH - ornament_r - 2, play_h - ornament_r - 2)]:
            pygame.draw.circle(self.screen, (80, 60, 38), (x, y), ornament_r, 2)
            pygame.draw.circle(self.screen, (50, 35, 22), (x, y), 3)

    def _update_and_draw_dust(self):
        """Update and draw ambient dust particles (screen-space)."""
        play_h = SCREEN_HEIGHT - HUD_PANEL_HEIGHT
        dust_surf = pygame.Surface((SCREEN_WIDTH, play_h), pygame.SRCALPHA)
        for p in self._dust_particles:
            # Gentle drift with sine wave wobble
            p["x"] += p["vx"] + math.sin(self.frame_count * 0.02 + p["drift_phase"]) * 0.1
            p["y"] += p["vy"]
            # Wrap around
            if p["x"] < -5:
                p["x"] = SCREEN_WIDTH + 5
            elif p["x"] > SCREEN_WIDTH + 5:
                p["x"] = -5
            if p["y"] < -5:
                p["y"] = play_h + 5
            elif p["y"] > play_h + 5:
                p["y"] = -5
            # Twinkle alpha
            a = int(p["alpha"] + 15 * math.sin(self.frame_count * 0.03 + p["drift_phase"]))
            a = max(10, min(60, a))
            pygame.draw.circle(dust_surf, (220, 210, 180, a),
                               (int(p["x"]), int(p["y"])), p["size"])
        self.screen.blit(dust_surf, (0, 0))

    def _spawn_animation(self, anim_event):
        """Create an animation from a game event."""
        anim = {
            "type": anim_event["type"],
            "world_row": anim_event["world_row"],
            "world_col": anim_event["world_col"],
            "frame": 0,
            "max_frames": 24,
            "damage": anim_event.get("damage", 0),
            # Pre-generate wobbly offsets for hand-drawn feel
            "wobble": [(random.randint(-2, 2), random.randint(-2, 2)) for _ in range(30)],
        }
        if anim_event["type"] == "death_poof":
            anim["max_frames"] = 30
            # Pre-generate splatter directions
            anim["splats"] = [(random.uniform(-1, 1), random.uniform(-1, 1),
                               random.randint(8, 20)) for _ in range(12)]
        elif anim_event["type"] == "level_up":
            anim["max_frames"] = 30
        elif anim_event["type"] == "fireball":
            anim["max_frames"] = 24
        elif anim_event["type"] == "trap_trigger":
            anim["max_frames"] = 20
            anim["splats"] = [(random.uniform(-1, 1), random.uniform(-1, 1),
                               random.randint(6, 15)) for _ in range(8)]
        self.animations.append(anim)

    def _draw_animations(self):
        """Draw and tick all active animations."""
        still_active = []
        for anim in self.animations:
            anim["frame"] += 1
            t = anim["frame"] / anim["max_frames"]  # 0.0 → 1.0
            sx, sy = self.camera.world_to_screen(anim["world_row"], anim["world_col"])
            cx = sx + TILE_SIZE // 2
            cy = sy + TILE_SIZE // 2

            if anim["type"] == "player_slash":
                self._draw_slash_animation(cx, cy, t, anim)
            elif anim["type"] == "monster_claw":
                self._draw_claw_animation(cx, cy, t, anim)
            elif anim["type"] == "death_poof":
                self._draw_death_animation(cx, cy, t, anim)
            elif anim["type"] == "level_up":
                self._draw_level_up_animation(cx, cy, t, anim)
            elif anim["type"] == "fireball":
                self._draw_fireball_animation(cx, cy, t, anim)
            elif anim["type"] == "trap_trigger":
                self._draw_trap_trigger_animation(cx, cy, t, anim)

            # Floating damage number (shared by slash and claw)
            if anim["type"] in ("player_slash", "monster_claw", "fireball", "trap_trigger") and anim["damage"] > 0:
                self._draw_damage_number(cx, cy, t, anim)

            if anim["frame"] < anim["max_frames"]:
                still_active.append(anim)
        self.animations = still_active

    def _draw_slash_animation(self, cx, cy, t, anim):
        """Hand-drawn sword slash — sweeping ink arc with speed lines."""
        size = TILE_SIZE * 1.8
        alpha = int(255 * (1.0 - t))
        surf = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
        scx, scy = int(size // 2), int(size // 2)
        wobble = anim["wobble"]

        # Phase 1 (0-0.5): Slash arc sweeps across
        # Phase 2 (0.5-1.0): Fade out with speed lines
        sweep = min(t * 2.0, 1.0)  # 0→1 during first half
        ink = (35, 30, 25, alpha)
        ink_light = (100, 90, 75, alpha)

        # Main slash arc — drawn as a series of connected line segments
        # Sweeps from top-left to bottom-right in an arc
        num_segments = int(sweep * 12) + 1
        arc_points = []
        for i in range(num_segments):
            angle = -2.2 + i * (2.8 / 12)
            r = int(size * 0.38)
            wx, wy = wobble[i % len(wobble)]
            px = scx + int(math.cos(angle) * r) + wx
            py = scy + int(math.sin(angle) * r) + wy
            arc_points.append((px, py))

        if len(arc_points) >= 2:
            # Thick main stroke (ink style, slightly wobbly)
            width = max(1, int(4 * (1.0 - t * 0.5)))
            pygame.draw.lines(surf, ink, False, arc_points, width)
            # Thinner parallel stroke for hand-drawn doubling
            offset_points = [(p[0] + 2, p[1] - 1) for p in arc_points]
            pygame.draw.lines(surf, ink_light, False, offset_points, max(1, width - 1))

        # Speed lines radiating from arc center (appear mid-animation)
        if t > 0.2:
            line_alpha = int(200 * (1.0 - t))
            for i in range(5):
                angle = -1.5 + i * 0.6
                wx, wy = wobble[(i + 5) % len(wobble)]
                r1 = int(size * 0.2)
                r2 = int(size * (0.3 + t * 0.15))
                x1 = scx + int(math.cos(angle) * r1) + wx
                y1 = scy + int(math.sin(angle) * r1) + wy
                x2 = scx + int(math.cos(angle) * r2) + wx
                y2 = scy + int(math.sin(angle) * r2) + wy
                pygame.draw.line(surf, (35, 30, 25, line_alpha), (x1, y1), (x2, y2), 1)

        # Impact burst at center (frame 3-10)
        if 3 <= anim["frame"] <= 14:
            burst_t = (anim["frame"] - 3) / 11.0
            burst_r = int(6 + burst_t * 10)
            burst_alpha = int(200 * (1.0 - burst_t))
            pygame.draw.circle(surf, (255, 240, 200, burst_alpha),
                               (scx, scy), burst_r, 2)

        blit_x = cx - int(size // 2)
        blit_y = cy - int(size // 2)
        self.screen.blit(surf, (blit_x, blit_y))

    def _draw_claw_animation(self, cx, cy, t, anim):
        """Hand-drawn claw scratch marks — three diagonal rakes."""
        size = TILE_SIZE * 1.5
        alpha = int(230 * (1.0 - t))
        surf = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
        scx, scy = int(size // 2), int(size // 2)
        wobble = anim["wobble"]

        scratch_len = min(t * 2.5, 1.0)  # Scratches extend quickly
        red_ink = (180, 40, 40, alpha)

        # Three parallel scratch lines
        for i in range(3):
            offset = (i - 1) * 10
            wx, wy = wobble[i]
            x1 = scx - 14 + offset + wx
            y1 = scy - 16 + wy
            x2 = x1 + int(28 * scratch_len)
            y2 = y1 + int(32 * scratch_len)
            # Draw with slight wobble for hand-drawn feel
            mid_x = (x1 + x2) // 2 + wobble[i + 3][0]
            mid_y = (y1 + y2) // 2 + wobble[i + 3][1]
            width = max(1, int(3 * (1.0 - t * 0.4)))
            pygame.draw.line(surf, red_ink, (x1, y1), (mid_x, mid_y), width)
            pygame.draw.line(surf, red_ink, (mid_x, mid_y), (x2, y2), width)

        # Blood drops (small circles that appear and fall)
        if t > 0.3:
            drop_t = (t - 0.3) / 0.7
            for i in range(4):
                dx = wobble[i + 6][0] * 3
                dy = int(drop_t * 15) + wobble[i + 6][1]
                drop_alpha = int(180 * (1.0 - drop_t))
                pygame.draw.circle(surf, (180, 40, 40, drop_alpha),
                                   (scx + dx, scy + dy), 2)

        blit_x = cx - int(size // 2)
        blit_y = cy - int(size // 2)
        self.screen.blit(surf, (blit_x, blit_y))

    def _draw_death_animation(self, cx, cy, t, anim):
        """Ink splatter burst when a monster dies."""
        size = TILE_SIZE * 2.2
        surf = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
        scx, scy = int(size // 2), int(size // 2)

        # Expanding ink splatters
        for dx, dy, max_dist in anim["splats"]:
            dist = t * max_dist * 3
            alpha = int(220 * (1.0 - t))
            px = scx + int(dx * dist)
            py = scy + int(dy * dist)
            blob_r = max(1, int(3 * (1.0 - t * 0.5)))
            pygame.draw.circle(surf, (35, 30, 25, alpha), (px, py), blob_r)
            # Trail line back to center
            if t < 0.6:
                trail_alpha = int(150 * (1.0 - t / 0.6))
                pygame.draw.line(surf, (35, 30, 25, trail_alpha),
                                 (scx, scy), (px, py), 1)

        # Central burst ring
        if t < 0.5:
            ring_r = int(t * 2 * size * 0.35)
            ring_alpha = int(200 * (1.0 - t * 2))
            pygame.draw.circle(surf, (80, 70, 60, ring_alpha),
                               (scx, scy), ring_r, 2)

        # "X" mark at center (ink cross that stays briefly)
        if t < 0.7:
            x_alpha = int(255 * (1.0 - t / 0.7))
            x_size = int(8 + t * 4)
            pygame.draw.line(surf, (35, 30, 25, x_alpha),
                             (scx - x_size, scy - x_size),
                             (scx + x_size, scy + x_size), 3)
            pygame.draw.line(surf, (35, 30, 25, x_alpha),
                             (scx + x_size, scy - x_size),
                             (scx - x_size, scy + x_size), 3)

        blit_x = cx - int(size // 2)
        blit_y = cy - int(size // 2)
        self.screen.blit(surf, (blit_x, blit_y))

    def _draw_damage_number(self, cx, cy, t, anim):
        """Floating damage number that rises and fades."""
        alpha = int(255 * (1.0 - t))
        float_y = cy - int(t * 40) - 20
        dmg_str = str(anim["damage"])

        if anim["type"] == "player_slash":
            color = (255, 255, 220)
            outline = (35, 30, 25)
        else:
            color = (255, 80, 80)
            outline = (80, 20, 20)

        # Render with outline (draw text offset in 4 dirs for outline, then center)
        text_surf = pygame.Surface((80, 50), pygame.SRCALPHA)
        text_surf.set_alpha(alpha)
        txt = self.font_damage.render(dmg_str, True, outline)
        tcx, tcy = 40, 25
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            text_surf.blit(txt, (tcx - txt.get_width() // 2 + ox,
                                 tcy - txt.get_height() // 2 + oy))
        txt2 = self.font_damage.render(dmg_str, True, color)
        text_surf.blit(txt2, (tcx - txt2.get_width() // 2,
                              tcy - txt2.get_height() // 2))

        self.screen.blit(text_surf, (cx - 40, float_y - 25))

    def _draw_fireball_animation(self, cx, cy, t, anim):
        """Fireball explosion — expanding fire ring with flame particles."""
        size = TILE_SIZE * 2.5
        surf = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
        scx, scy = int(size // 2), int(size // 2)
        alpha = int(255 * (1.0 - t))

        # Expanding fire ring
        ring_r = int(10 + t * size * 0.35)
        ring_w = max(1, int(4 * (1.0 - t)))
        pygame.draw.circle(surf, (255, 120, 30, alpha), (scx, scy), ring_r, ring_w)

        # Inner glow
        if t < 0.5:
            glow_r = int(ring_r * 0.6)
            glow_alpha = int(150 * (1.0 - t * 2))
            pygame.draw.circle(surf, (255, 200, 80, glow_alpha), (scx, scy), glow_r)

        # Flame particles
        wobble = anim.get("wobble", [(0, 0)] * 16)
        for i in range(8):
            angle = i * (math.pi / 4) + t * 2
            r = ring_r * 0.8
            wx, wy = wobble[i % len(wobble)]
            px = scx + int(math.cos(angle) * r) + wx
            py = scy + int(math.sin(angle) * r) + wy
            flame_alpha = int(200 * (1.0 - t))
            pygame.draw.circle(surf, (255, 80, 20, flame_alpha), (px, py), 3)

        blit_x = cx - int(size // 2)
        blit_y = cy - int(size // 2)
        self.screen.blit(surf, (blit_x, blit_y))

    def _draw_trap_trigger_animation(self, cx, cy, t, anim):
        """Trap trigger — green-brown flash with splatter."""
        size = TILE_SIZE * 2.0
        surf = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
        scx, scy = int(size // 2), int(size // 2)
        alpha = int(220 * (1.0 - t))

        # Expanding ring (green-brown)
        ring_r = int(8 + t * size * 0.3)
        ring_w = max(1, int(3 * (1.0 - t)))
        pygame.draw.circle(surf, (100, 160, 60, alpha), (scx, scy), ring_r, ring_w)

        # Splatter particles
        for dx, dy, max_dist in anim.get("splats", []):
            dist = t * max_dist * 2.5
            p_alpha = int(200 * (1.0 - t))
            px = scx + int(dx * dist)
            py = scy + int(dy * dist)
            blob_r = max(1, int(2 * (1.0 - t * 0.5)))
            pygame.draw.circle(surf, (80, 120, 40, p_alpha), (px, py), blob_r)

        # Central flash
        if t < 0.3:
            flash_alpha = int(180 * (1.0 - t / 0.3))
            pygame.draw.circle(surf, (200, 180, 80, flash_alpha), (scx, scy), int(8 * (1.0 - t)))

        blit_x = cx - int(size // 2)
        blit_y = cy - int(size // 2)
        self.screen.blit(surf, (blit_x, blit_y))

    def _draw_torch_glow(self, players):
        """Draw torch glow effect around alive players using pre-rendered surface."""
        glow_radius = TILE_SIZE * 3
        for player in players:
            if not player.is_alive():
                continue
            sx, sy = self.camera.world_to_screen(player.world_row, player.world_col)
            cx = sx + TILE_SIZE // 2
            cy = sy + TILE_SIZE // 2

            # Flicker: slight size and position variation
            flicker_x = int(math.sin(self.frame_count * 0.1 + player.player_id * 2.0) * 4)
            flicker_y = int(math.cos(self.frame_count * 0.13 + player.player_id * 1.5) * 3)
            # Intensity flicker
            flicker_alpha = int(220 + 35 * math.sin(self.frame_count * 0.15 + player.player_id))
            glow = self._torch_glow_surf.copy()
            glow.set_alpha(min(255, flicker_alpha))
            self.screen.blit(glow, (cx - glow_radius + flicker_x,
                                     cy - glow_radius + flicker_y))

    def _draw_traps(self, game_logic):
        """Draw placed traps on the map."""
        if not hasattr(game_logic, 'traps'):
            return
        for trap in game_logic.traps:
            sx, sy = self.camera.world_to_screen(trap["row"], trap["col"])
            trap_cx, trap_cy = sx + TILE_SIZE // 2, sy + TILE_SIZE // 2
            # Small jagged circle (bear trap look)
            pygame.draw.circle(self.screen, COLOR_INK_LIGHT, (trap_cx, trap_cy), 8, 1)
            # Teeth
            for angle_off in range(0, 360, 45):
                a = math.radians(angle_off)
                x1 = trap_cx + int(math.cos(a) * 8)
                y1 = trap_cy + int(math.sin(a) * 8)
                x2 = trap_cx + int(math.cos(a) * 12)
                y2 = trap_cy + int(math.sin(a) * 12)
                pygame.draw.line(self.screen, COLOR_INK_LIGHT, (x1, y1), (x2, y2), 1)

    def _draw_level_up_animation(self, cx, cy, t, anim):
        """Golden ring expanding outward with LEVEL UP text floating up."""
        gold = (255, 200, 80)
        alpha = int(255 * (1.0 - t))
        # Expanding ring
        ring_r = int(10 + t * 30)
        ring_w = max(1, int(3 * (1.0 - t)))
        ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*gold, alpha),
                           (ring_r + 2, ring_r + 2), ring_r, ring_w)
        self.screen.blit(ring_surf, (cx - ring_r - 2, cy - ring_r - 2))
        # "LEVEL UP!" text floating upward
        float_y = cy - int(t * 35) - 20
        txt = self.font_medium.render("LEVEL UP!", True, gold)
        txt_surf = pygame.Surface((txt.get_width() + 4, txt.get_height() + 4),
                                  pygame.SRCALPHA)
        txt_surf.set_alpha(alpha)
        # Outline
        outline = self.font_medium.render("LEVEL UP!", True, (35, 30, 25))
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            txt_surf.blit(outline, (2 + ox, 2 + oy))
        txt_surf.blit(txt, (2, 2))
        self.screen.blit(txt_surf, (cx - txt.get_width() // 2 - 2, float_y))

    def _draw_hover_effects(self, player, highlights):
        """Draw movement path preview and contextual hover icons."""
        if not player or player.action_points <= 0:
            return

        mouse_pos = pygame.mouse.get_pos()
        # Only process hover in map area (above HUD)
        if mouse_pos[1] >= SCREEN_HEIGHT - HUD_PANEL_HEIGHT:
            return

        world_row, world_col = self.camera.screen_to_world(mouse_pos[0], mouse_pos[1])
        hovered = (world_row, world_col)

        # Determine hover type (priority: attack > door > chest > move)
        hover_type = None
        if hovered in highlights.get("attack", []):
            hover_type = "attack"
        elif hovered in highlights.get("door", []):
            hover_type = "door"
        elif hovered in highlights.get("chest", []):
            hover_type = "chest"
        elif hovered in highlights.get("move", []):
            hover_type = "move"

        if hover_type is None:
            return

        sx, sy = self.camera.world_to_screen(world_row, world_col)
        tile_cx = sx + TILE_SIZE // 2
        tile_cy = sy + TILE_SIZE // 2

        # Draw movement path preview (dotted line from player to hovered tile)
        if hover_type == "move":
            player_sx, player_sy = self.camera.world_to_screen(
                player.world_row, player.world_col)
            px = player_sx + TILE_SIZE // 2
            py = player_sy + TILE_SIZE // 2
            dx = tile_cx - px
            dy = tile_cy - py
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                dot_spacing = 16
                num_dots = int(dist / dot_spacing)
                dot_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
                for i in range(1, num_dots + 1):
                    t = i / max(num_dots, 1)
                    dot_x = int(px + dx * t)
                    dot_y = int(py + dy * t)
                    pygame.draw.circle(self.screen, (180, 160, 120, 200),
                                       (dot_x, dot_y), 3)

        # Draw contextual hover icon
        if hover_type != "move":
            self._draw_hover_icon(hover_type, tile_cx, tile_cy)

    def _draw_hover_icon(self, hover_type, sx, sy):
        """Draw a contextual icon at the given screen position."""
        icon_surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        cx, cy = 24, 24
        ink = (35, 30, 25, 200)

        if hover_type == "attack":
            # Crossed swords
            pygame.draw.line(icon_surf, ink, (cx - 10, cy - 10), (cx + 10, cy + 10), 2)
            pygame.draw.line(icon_surf, ink, (cx + 10, cy - 10), (cx - 10, cy + 10), 2)
            # Pommels
            pygame.draw.circle(icon_surf, ink, (cx - 10, cy - 10), 3, 1)
            pygame.draw.circle(icon_surf, ink, (cx + 10, cy - 10), 3, 1)
            # Guard lines
            pygame.draw.line(icon_surf, ink, (cx - 5, cy - 5), (cx - 1, cy - 9), 2)
            pygame.draw.line(icon_surf, ink, (cx + 5, cy - 5), (cx + 1, cy - 9), 2)

        elif hover_type == "chest":
            # Open chest body
            body = pygame.Rect(cx - 12, cy - 2, 24, 14)
            pygame.draw.rect(icon_surf, (180, 150, 60, 180), body)
            pygame.draw.rect(icon_surf, ink, body, 2)
            # Angled lid
            pygame.draw.line(icon_surf, ink, (cx - 12, cy - 2), (cx - 10, cy - 10), 2)
            pygame.draw.line(icon_surf, ink, (cx - 10, cy - 10), (cx + 10, cy - 10), 2)
            pygame.draw.line(icon_surf, ink, (cx + 10, cy - 10), (cx + 12, cy - 2), 2)
            # Sparkle
            pygame.draw.line(icon_surf, (255, 220, 80, 200),
                             (cx, cy - 14), (cx, cy - 18), 1)
            pygame.draw.line(icon_surf, (255, 220, 80, 200),
                             (cx - 2, cy - 16), (cx + 2, cy - 16), 1)

        elif hover_type == "door":
            # Door rectangle
            door = pygame.Rect(cx - 8, cy - 12, 16, 24)
            pygame.draw.rect(icon_surf, (160, 130, 80, 180), door)
            pygame.draw.rect(icon_surf, ink, door, 2)
            # Handle
            pygame.draw.circle(icon_surf, ink, (cx + 4, cy), 2, 1)
            # Arrow pointing right
            pygame.draw.line(icon_surf, ink, (cx + 12, cy), (cx + 20, cy), 2)
            pygame.draw.line(icon_surf, ink, (cx + 17, cy - 3), (cx + 20, cy), 2)
            pygame.draw.line(icon_surf, ink, (cx + 17, cy + 3), (cx + 20, cy), 2)

        self.screen.blit(icon_surf, (sx - 24, sy - 24))

    def _draw_hud(self, players, game_logic):
        """Draw the HUD panel styled as a board game card."""
        panel_y = SCREEN_HEIGHT - HUD_PANEL_HEIGHT
        panel_rect = pygame.Rect(0, panel_y, SCREEN_WIDTH, HUD_PANEL_HEIGHT)

        # Card-style drop shadow at top
        shadow_h = 6
        shadow_surf = pygame.Surface((SCREEN_WIDTH, shadow_h), pygame.SRCALPHA)
        for i in range(shadow_h):
            a = 60 * (shadow_h - i) // shadow_h
            pygame.draw.line(shadow_surf, (20, 15, 10, a),
                             (0, i), (SCREEN_WIDTH, i))
        self.screen.blit(shadow_surf, (0, panel_y - shadow_h))

        # Cream card edge strip
        edge_rect = pygame.Rect(0, panel_y - 3, SCREEN_WIDTH, HUD_PANEL_HEIGHT + 3)
        pygame.draw.rect(self.screen, COLOR_CARD_EDGE, edge_rect)

        # Parchment background (main card body)
        pygame.draw.rect(self.screen, COLOR_PARCHMENT, panel_rect)

        # Cross-hatch shading along top 10px
        for i in range(0, SCREEN_WIDTH + 10, 6):
            pygame.draw.line(self.screen, COLOR_PARCHMENT_DARK,
                             (i, panel_y), (i - 10, panel_y + 10), 1)

        # Double ink border at top
        pygame.draw.line(self.screen, COLOR_INK,
                         (0, panel_y), (SCREEN_WIDTH, panel_y), 2)
        pygame.draw.line(self.screen, COLOR_INK,
                         (0, panel_y + 4), (SCREEN_WIDTH, panel_y + 4), 1)

        # Corner scroll flourishes (arcs at top corners)
        arc_size = 20
        # Top-left flourish
        pygame.draw.arc(self.screen, COLOR_INK,
                        pygame.Rect(0, panel_y - 5, arc_size, arc_size),
                        -0.5, 1.2, 2)
        # Top-right flourish
        pygame.draw.arc(self.screen, COLOR_INK,
                        pygame.Rect(SCREEN_WIDTH - arc_size, panel_y - 5,
                                    arc_size, arc_size),
                        1.9, 3.6, 2)

        # === LEFT SECTION: Player info ===
        player = game_logic.get_current_player()
        if player:
            y_base = panel_y + 12

            # Player name with level badge (underlined with ink)
            name_str = f"P{player.player_id + 1} - {player.character_type}"
            name_text = self.font_large.render(name_str, True, player.color)
            self.screen.blit(name_text, (15, y_base))
            name_w = name_text.get_width()
            # Level badge
            lv_str = f"Lv{player.level}"
            lv_text = self.font_small.render(lv_str, True, COLOR_UI_HIGHLIGHT)
            self.screen.blit(lv_text, (15 + name_w + 6, y_base + 8))
            pygame.draw.line(self.screen, COLOR_INK,
                             (15, y_base + name_text.get_height()),
                             (15 + name_w, y_base + name_text.get_height()), 1)

            # HP bar with heart prefix
            hp_y = y_base + 38
            # Heart symbol (drawn as small triangle + circle)
            hx = 15
            pygame.draw.polygon(self.screen, (200, 40, 40),
                                [(hx + 6, hp_y + 12), (hx, hp_y + 5), (hx + 12, hp_y + 5)])
            pygame.draw.circle(self.screen, (200, 40, 40), (hx + 3, hp_y + 4), 3)
            pygame.draw.circle(self.screen, (200, 40, 40), (hx + 9, hp_y + 4), 3)

            bar_x = 32
            bar_w = 200
            bar_h = 16
            # Bar shadow
            pygame.draw.rect(self.screen, (40, 30, 30),
                             pygame.Rect(bar_x + 1, hp_y + 1, bar_w, bar_h),
                             border_radius=3)
            # Bar background
            pygame.draw.rect(self.screen, COLOR_HEALTH_BG,
                             pygame.Rect(bar_x, hp_y, bar_w, bar_h),
                             border_radius=3)
            # Gradient bar fill
            hp_ratio = player.health / player.max_health if player.max_health > 0 else 0
            fill_w = int(bar_w * hp_ratio)
            if fill_w > 0:
                fill_surf = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
                for i in range(bar_h):
                    t = i / bar_h
                    r = int(100 + 100 * (1.0 - t * 0.5))
                    g = int(30 + 20 * (1.0 - t))
                    b = int(30 + 10 * (1.0 - t))
                    pygame.draw.line(fill_surf, (r, g, b), (0, i), (fill_w, i))
                # Top highlight
                pygame.draw.line(fill_surf, (240, 100, 100), (1, 1), (fill_w - 1, 1), 1)
                self.screen.blit(fill_surf, (bar_x, hp_y))
            # Ink border
            pygame.draw.rect(self.screen, COLOR_INK,
                             pygame.Rect(bar_x, hp_y, bar_w, bar_h), 2,
                             border_radius=3)
            # HP text on bar
            hp_str = f"{player.health}/{player.max_health}"
            hp_text = self.font_small.render(hp_str, True, (255, 255, 255))
            self.screen.blit(hp_text, (bar_x + bar_w // 2 - hp_text.get_width() // 2,
                                       hp_y + 1))

            # XP bar (below HP bar, gradient purple)
            xp_y = hp_y + bar_h + 3
            xp_bar_h = 6
            pygame.draw.rect(self.screen, (40, 35, 50),
                             pygame.Rect(bar_x, xp_y, bar_w, xp_bar_h),
                             border_radius=2)
            xp_ratio = player.xp / player.xp_to_next if player.xp_to_next > 0 else 0
            xp_fill = int(bar_w * xp_ratio)
            if xp_fill > 0:
                for i in range(xp_bar_h):
                    t = i / xp_bar_h
                    r = int(120 + 40 * (1.0 - t))
                    g = int(80 + 30 * (1.0 - t))
                    b = int(180 + 30 * (1.0 - t))
                    pygame.draw.line(self.screen, (r, g, b),
                                     (bar_x, xp_y + i), (bar_x + xp_fill, xp_y + i))
            pygame.draw.rect(self.screen, COLOR_INK,
                             pygame.Rect(bar_x, xp_y, bar_w, xp_bar_h), 1,
                             border_radius=2)
            xp_label = self.font_tiny.render(
                f"XP {player.xp}/{player.xp_to_next}", True, COLOR_INK)
            self.screen.blit(xp_label, (bar_x + bar_w + 4, xp_y))

            # AP pips
            ap_y = hp_y + 22
            ap_label = self.font_small.render("AP", True, COLOR_INK)
            self.screen.blit(ap_label, (15, ap_y))
            for i in range(player.max_action_points):
                pip_x = 38 + i * 40
                pip_rect = pygame.Rect(pip_x, ap_y, 36, 16)
                if i < player.action_points:
                    pygame.draw.rect(self.screen, COLOR_AP_BAR, pip_rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_PARCHMENT_DARK, pip_rect)
                pygame.draw.rect(self.screen, COLOR_INK, pip_rect, 1)

            # Stats row with drawn icons
            stat_y = ap_y + 22
            stat_x = 15

            # Attack icon (small sword: two lines)
            pygame.draw.line(self.screen, COLOR_INK,
                             (stat_x, stat_y + 10), (stat_x + 10, stat_y), 2)
            pygame.draw.line(self.screen, COLOR_INK,
                             (stat_x + 7, stat_y + 2), (stat_x + 12, stat_y + 5), 1)
            atk_text = self.font_small.render(f" {player.attack}", True, COLOR_INK)
            self.screen.blit(atk_text, (stat_x + 12, stat_y))
            stat_x += 45

            # Keys icon (circle + line)
            pygame.draw.circle(self.screen, COLOR_INK, (stat_x + 4, stat_y + 4), 4, 1)
            pygame.draw.line(self.screen, COLOR_INK,
                             (stat_x + 4, stat_y + 8), (stat_x + 4, stat_y + 14), 2)
            key_text = self.font_small.render(f" {player.keys}", True, COLOR_INK)
            self.screen.blit(key_text, (stat_x + 10, stat_y))
            stat_x += 40

            # Gold icon (filled circle)
            pygame.draw.circle(self.screen, (200, 180, 50), (stat_x + 5, stat_y + 6), 5)
            pygame.draw.circle(self.screen, COLOR_INK, (stat_x + 5, stat_y + 6), 5, 1)
            gold_text = self.font_small.render(f" {player.gold}", True, COLOR_INK)
            self.screen.blit(gold_text, (stat_x + 12, stat_y))
            stat_x += 45

            # Potion icon (red cross + count)
            px = stat_x
            pygame.draw.line(self.screen, (200, 40, 40),
                             (px + 4, stat_y + 2), (px + 4, stat_y + 12), 3)
            pygame.draw.line(self.screen, (200, 40, 40),
                             (px, stat_y + 7), (px + 8, stat_y + 7), 3)
            pot_text = self.font_small.render(
                f" x{player.potions}", True, COLOR_INK)
            self.screen.blit(pot_text, (px + 10, stat_y))
            stat_x += 45

            # Weapon
            weapon_str = player.weapon if player.weapon else "None"
            wpn_text = self.font_small.render(f"Wpn: {weapon_str}", True, COLOR_INK)
            self.screen.blit(wpn_text, (stat_x, stat_y))

        # === CENTER SECTION: Phase text ===
        # (Phase is drawn in _draw_round_banner instead)

        # === RIGHT SECTION: Round + Cards info ===
        right_x = SCREEN_WIDTH - 170
        right_y = panel_y + 15
        round_text = self.font_medium.render(
            f"Round {game_logic.round_number}", True, COLOR_INK)
        self.screen.blit(round_text, (right_x, right_y))

        cards_text = self.font_small.render(
            f"Cards: {game_logic.world.deck.cards_drawn}", True, COLOR_INK)
        self.screen.blit(cards_text, (right_x, right_y + 28))

    def _draw_round_banner(self, game_logic):
        """Draw the round/phase banner as a card-style tag at top-center."""
        banner_w = 220
        banner_h = 36
        bx = SCREEN_WIDTH // 2 - banner_w // 2
        by = 4

        # Drop shadow
        shadow_surf = pygame.Surface((banner_w + 6, banner_h + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (20, 15, 10, 80),
                         pygame.Rect(3, 3, banner_w, banner_h),
                         border_radius=6)
        self.screen.blit(shadow_surf, (bx - 2, by - 1))

        # Card edge
        edge_rect = pygame.Rect(bx - 2, by - 2, banner_w + 4, banner_h + 4)
        pygame.draw.rect(self.screen, COLOR_CARD_EDGE, edge_rect, border_radius=8)

        # Banner background (parchment)
        banner_rect = pygame.Rect(bx, by, banner_w, banner_h)
        pygame.draw.rect(self.screen, COLOR_PARCHMENT, banner_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_INK, banner_rect, 2, border_radius=6)

        # Phase text
        if game_logic.is_monster_phase:
            phase_str = "Monster Turn"
            phase_color = (200, 50, 50)
        else:
            phase_str = f"Player {game_logic.current_player_index + 1}'s Turn"
            phase_color = COLOR_UI_HIGHLIGHT
        phase_text = self.font_medium.render(phase_str, True, phase_color)
        self.screen.blit(phase_text,
                         (SCREEN_WIDTH // 2 - phase_text.get_width() // 2, by + 6))

    def _draw_message_log(self, game_logic):
        """Draw message log on right side of HUD with parchment background."""
        panel_y = SCREEN_HEIGHT - HUD_PANEL_HEIGHT
        x = SCREEN_WIDTH - 350
        y = panel_y + 15
        log_w = 180
        log_h = HUD_PANEL_HEIGHT - 20
        messages = game_logic.message_log[-5:]
        if not messages:
            return

        # Semi-transparent parchment bg
        bg_surf = pygame.Surface((log_w, log_h), pygame.SRCALPHA)
        bg_surf.fill((235, 225, 200, 180))
        self.screen.blit(bg_surf, (x - 5, y - 5))
        pygame.draw.rect(self.screen, COLOR_INK_LIGHT,
                         pygame.Rect(x - 5, y - 5, log_w, log_h), 1)

        for i, msg in enumerate(messages):
            # Truncate long messages
            display_msg = msg if len(msg) < 28 else msg[:25] + "..."
            text = self.font_small.render(display_msg, True, COLOR_INK)
            self.screen.blit(text, (x, y + i * 18))

    def render_skip_button(self, game_logic):
        """Render skip turn button (parchment style) and return its rect."""
        buttons = []
        player = game_logic.get_current_player()
        if not player or not game_logic.is_player_phase:
            return buttons

        button_y = SCREEN_HEIGHT - HUD_PANEL_HEIGHT + 25
        button_x = SCREEN_WIDTH - 110
        button_w = 90
        button_h = 32

        rect = pygame.Rect(button_x, button_y, button_w, button_h)
        mouse_pos = pygame.mouse.get_pos()

        # Parchment button with ink border
        bg_color = COLOR_PARCHMENT_DARK if rect.collidepoint(mouse_pos) else COLOR_PARCHMENT
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_INK, rect, 2, border_radius=4)

        text = self.font_small.render(STRINGS["skip_turn"], True, COLOR_INK)
        self.screen.blit(text, (button_x + button_w // 2 - text.get_width() // 2,
                                button_y + button_h // 2 - text.get_height() // 2))
        buttons.append((rect, "skip"))

        return buttons

    def render_skill_buttons(self, game_logic):
        """Render skill buttons in the HUD and return clickable rects."""
        buttons = []
        player = game_logic.get_current_player()
        if not player or not game_logic.is_player_phase:
            return buttons

        panel_y = SCREEN_HEIGHT - HUD_PANEL_HEIGHT

        for i, skill in enumerate(player.skills):
            btn_x = SCREEN_WIDTH - 220 + i * 105
            btn_y = panel_y + 65
            btn_w = 100
            btn_h = 55

            rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            mouse_pos = pygame.mouse.get_pos()

            can_use = player.can_use_skill(i)

            # Button background
            if not can_use:
                bg = (180, 170, 150)
            elif rect.collidepoint(mouse_pos):
                bg = COLOR_PARCHMENT_DARK
            else:
                bg = COLOR_PARCHMENT

            pygame.draw.rect(self.screen, bg, rect, border_radius=4)
            pygame.draw.rect(self.screen, COLOR_INK, rect, 2, border_radius=4)

            # Key binding
            key_text = self.font_small.render(f"[{skill['key']}]", True, COLOR_INK_LIGHT)
            self.screen.blit(key_text, (btn_x + 3, btn_y + 3))

            # Skill name (truncated)
            name = skill["name"]
            if len(name) > 12:
                name = name[:11] + "."
            name_text = self.font_small.render(name, True, COLOR_INK)
            self.screen.blit(name_text, (btn_x + btn_w // 2 - name_text.get_width() // 2,
                                         btn_y + 18))

            # AP cost
            ap_text = self.font_small.render(f"{skill['ap_cost']} AP", True, COLOR_INK_LIGHT)
            self.screen.blit(ap_text, (btn_x + btn_w // 2 - ap_text.get_width() // 2,
                                       btn_y + 35))

            # Cooldown overlay
            cd = player.skill_cooldowns[i]
            if cd > 0:
                cd_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                cd_surf.fill((0, 0, 0, 120))
                self.screen.blit(cd_surf, (btn_x, btn_y))
                cd_text = self.font_medium.render(str(cd), True, (255, 200, 80))
                self.screen.blit(cd_text, (btn_x + btn_w // 2 - cd_text.get_width() // 2,
                                           btn_y + btn_h // 2 - cd_text.get_height() // 2))

            buttons.append((rect, f"skill_{i}"))

        return buttons

    def draw_skill_hint(self, text):
        """Draw skill targeting hint at top of screen."""
        hint_surf = self.font_medium.render(text, True, (255, 220, 100))
        bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - hint_surf.get_width() // 2 - 10,
                              8, hint_surf.get_width() + 20, hint_surf.get_height() + 8)
        bg = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg.fill((35, 30, 25, 180))
        self.screen.blit(bg, bg_rect)
        self.screen.blit(hint_surf, (bg_rect.x + 10, bg_rect.y + 4))

    def render_menu(self):
        """Render main menu as a board game box cover."""
        self._draw_table_background()

        # Central card panel (like a game box)
        card_w, card_h = 500, 400
        card_x = SCREEN_WIDTH // 2 - card_w // 2
        card_y = SCREEN_HEIGHT // 2 - card_h // 2 - 20
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        self._draw_card_panel(card_rect, radius=12)

        # Ornate double border inside card
        inner = pygame.Rect(card_x + 12, card_y + 12, card_w - 24, card_h - 24)
        pygame.draw.rect(self.screen, COLOR_INK, inner, 2, border_radius=8)
        inner2 = pygame.Rect(card_x + 16, card_y + 16, card_w - 32, card_h - 32)
        pygame.draw.rect(self.screen, COLOR_INK_LIGHT, inner2, 1, border_radius=6)

        # Corner flourishes
        for cx, cy in [(card_x + 20, card_y + 20), (card_x + card_w - 20, card_y + 20),
                        (card_x + 20, card_y + card_h - 20), (card_x + card_w - 20, card_y + card_h - 20)]:
            pygame.draw.circle(self.screen, COLOR_INK, (cx, cy), 4, 1)
            pygame.draw.circle(self.screen, COLOR_INK, (cx, cy), 2)

        # Title
        title = self.font_title.render(STRINGS["title"], True, COLOR_INK)
        self.screen.blit(title,
                         (SCREEN_WIDTH // 2 - title.get_width() // 2, card_y + 50))

        # Decorative line under title
        line_y = card_y + 50 + title.get_height() + 5
        pygame.draw.line(self.screen, COLOR_INK,
                         (card_x + 60, line_y), (card_x + card_w - 60, line_y), 2)

        # Subtitle
        subtitle = self.font_medium.render(
            "A dungeon crawling board game", True, COLOR_INK_LIGHT)
        self.screen.blit(subtitle,
                         (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, line_y + 12))

        # Buttons
        buttons = []
        mouse_pos = pygame.mouse.get_pos()
        button_labels = [
            (STRINGS["start_game"], "start"),
            (STRINGS["quit"], "quit"),
        ]

        for i, (label, action) in enumerate(button_labels):
            btn_y = card_y + 200 + i * 60
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, btn_y, 200, 45)
            is_hover = rect.collidepoint(mouse_pos)
            # Card-style button
            if is_hover:
                bg = COLOR_PARCHMENT_DARK
            else:
                bg = COLOR_PARCHMENT
            # Small shadow
            shadow = pygame.Surface((204, 49), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (20, 15, 10, 60),
                             pygame.Rect(2, 2, 200, 45), border_radius=6)
            self.screen.blit(shadow, (rect.x, rect.y))
            pygame.draw.rect(self.screen, COLOR_CARD_EDGE,
                             pygame.Rect(rect.x - 2, rect.y - 2, 204, 49),
                             border_radius=8)
            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, COLOR_INK, rect, 2, border_radius=6)
            text = self.font_medium.render(label, True, COLOR_INK)
            self.screen.blit(text, (rect.centerx - text.get_width() // 2,
                                    rect.centery - text.get_height() // 2))
            buttons.append((rect, action))

        return buttons

    def render_mode_select(self):
        """Render game mode selection screen."""
        self._draw_table_background()

        # Card panel
        card_w, card_h = 500, 400
        card_x = SCREEN_WIDTH // 2 - card_w // 2
        card_y = 60
        self._draw_card_panel(pygame.Rect(card_x, card_y, card_w, card_h), radius=10)

        # Title
        title = self.font_large.render("Choose Game Mode", True, COLOR_INK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, card_y + 25))

        buttons = []
        mouse_pos = pygame.mouse.get_pos()

        # Single player button (card style)
        single_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, card_y + 80, 300, 80)
        bg = COLOR_PARCHMENT_DARK if single_rect.collidepoint(mouse_pos) else COLOR_PARCHMENT
        pygame.draw.rect(self.screen, COLOR_CARD_EDGE,
                         pygame.Rect(single_rect.x - 2, single_rect.y - 2, 304, 84),
                         border_radius=10)
        pygame.draw.rect(self.screen, bg, single_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_INK, single_rect, 2, border_radius=8)
        st = self.font_medium.render("Single Player", True, COLOR_INK)
        sd = self.font_small.render("One hero enters the dungeon alone", True, COLOR_INK_LIGHT)
        self.screen.blit(st, (single_rect.centerx - st.get_width() // 2,
                              single_rect.y + 18))
        self.screen.blit(sd, (single_rect.centerx - sd.get_width() // 2,
                              single_rect.y + 50))
        buttons.append((single_rect, "single"))

        # Multiplayer button (card style)
        multi_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, card_y + 180, 300, 80)
        bg = COLOR_PARCHMENT_DARK if multi_rect.collidepoint(mouse_pos) else COLOR_PARCHMENT
        pygame.draw.rect(self.screen, COLOR_CARD_EDGE,
                         pygame.Rect(multi_rect.x - 2, multi_rect.y - 2, 304, 84),
                         border_radius=10)
        pygame.draw.rect(self.screen, bg, multi_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_INK, multi_rect, 2, border_radius=8)
        mt = self.font_medium.render("Multiplayer (2-4)", True, COLOR_INK)
        md = self.font_small.render("Brave the dungeon with friends", True, COLOR_INK_LIGHT)
        self.screen.blit(mt, (multi_rect.centerx - mt.get_width() // 2,
                              multi_rect.y + 18))
        self.screen.blit(md, (multi_rect.centerx - md.get_width() // 2,
                              multi_rect.y + 50))
        buttons.append((multi_rect, "multi"))

        # Back button (card style)
        back_rect = pygame.Rect(card_x + 10, card_y + card_h - 50, 80, 35)
        pygame.draw.rect(self.screen, COLOR_PARCHMENT_DARK, back_rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_INK, back_rect, 1, border_radius=4)
        bt = self.font_small.render(STRINGS["back"], True, COLOR_UI_TEXT)
        self.screen.blit(bt, (back_rect.centerx - bt.get_width() // 2,
                              back_rect.centery - bt.get_height() // 2))
        buttons.append((back_rect, "back"))

        return buttons

    def render_character_select(self, num_players, selected_characters):
        """Render character selection screen as playing cards on table."""
        self._draw_table_background()

        # Title on a small card tag
        title_w = 340
        title_rect = pygame.Rect(SCREEN_WIDTH // 2 - title_w // 2, 10, title_w, 40)
        self._draw_card_panel(title_rect, radius=6)
        title = self.font_large.render(STRINGS["select_character"], True, COLOR_INK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 16))

        # Player count on small card
        count_rect = pygame.Rect(30, 65, 220, 35)
        self._draw_card_panel(count_rect, radius=4)
        players_text = self.font_medium.render(
            f"Players: {num_players}", True, COLOR_INK)
        self.screen.blit(players_text, (40, 72))

        buttons = []
        mouse_pos = pygame.mouse.get_pos()

        # Player count buttons (card tokens)
        for i in range(1, 5):
            rect = pygame.Rect(260 + (i - 1) * 50, 70, 40, 30)
            selected = (i == num_players)
            if selected:
                bg = COLOR_UI_HIGHLIGHT
            elif rect.collidepoint(mouse_pos):
                bg = COLOR_PARCHMENT_DARK
            else:
                bg = COLOR_PARCHMENT
            pygame.draw.rect(self.screen, COLOR_CARD_EDGE,
                             pygame.Rect(rect.x - 1, rect.y - 1, 42, 32),
                             border_radius=5)
            pygame.draw.rect(self.screen, bg, rect, border_radius=4)
            pygame.draw.rect(self.screen, COLOR_INK, rect, 1, border_radius=4)
            text = self.font_small.render(str(i), True,
                                          (35, 30, 25) if selected else COLOR_INK)
            self.screen.blit(text, (rect.centerx - text.get_width() // 2,
                                    rect.centery - text.get_height() // 2))
            buttons.append((rect, f"players_{i}"))

        # Character cards (playing card style on table)
        from constants import CHARACTERS
        card_width = 300
        card_height = 350
        start_x = (SCREEN_WIDTH - len(CHARACTERS) * (card_width + 20)) // 2
        y = 130

        for idx, (char_name, stats) in enumerate(CHARACTERS.items()):
            cx = start_x + idx * (card_width + 20)
            card_rect = pygame.Rect(cx, y, card_width, card_height)

            is_selected = char_name in selected_characters

            # Card with shadow + cream edge
            self._draw_card_panel(card_rect, radius=10)

            # Selected highlight border
            if is_selected:
                pygame.draw.rect(self.screen, COLOR_UI_HIGHLIGHT, card_rect, 3,
                                 border_radius=10)
            else:
                pygame.draw.rect(self.screen, COLOR_INK, card_rect, 1,
                                 border_radius=10)

            # Inner decorative border
            inner_rect = pygame.Rect(cx + 8, y + 8, card_width - 16, card_height - 16)
            pygame.draw.rect(self.screen, COLOR_INK_LIGHT, inner_rect, 1,
                             border_radius=6)

            # Character name (dark ink on parchment)
            name = self.font_large.render(char_name, True, stats["color"])
            self.screen.blit(name, (cx + card_width // 2 - name.get_width() // 2, y + 15))

            # Character avatar (circle with card-edge ring)
            avatar_cx = cx + card_width // 2
            avatar_cy = y + 100
            pygame.draw.circle(self.screen, COLOR_CARD_EDGE, (avatar_cx, avatar_cy), 42)
            pygame.draw.circle(self.screen, stats["color"], (avatar_cx, avatar_cy), 40)
            pygame.draw.circle(self.screen, COLOR_INK, (avatar_cx, avatar_cy), 42, 2)

            # Stats
            stat_y = y + 160
            stat_labels = [
                f"Attack: {stats['attack']}",
                f"Health: {stats['health']}",
                f"Action Points: {stats['action_points']}",
                f"Speed: {stats['speed']}",
            ]
            for si, stat_label in enumerate(stat_labels):
                st = self.font_medium.render(stat_label, True, COLOR_INK)
                self.screen.blit(st, (cx + 20, stat_y + si * 30))

            # Description
            desc = self.font_small.render(stats["description"], True, COLOR_INK_LIGHT)
            self.screen.blit(desc, (cx + 20, stat_y + 130))

            # Select button (card style)
            btn_rect = pygame.Rect(cx + 50, y + card_height - 50, card_width - 100, 35)
            if is_selected:
                btn_bg = COLOR_UI_HIGHLIGHT
            elif btn_rect.collidepoint(mouse_pos):
                btn_bg = COLOR_PARCHMENT_DARK
            else:
                btn_bg = COLOR_PARCHMENT
            pygame.draw.rect(self.screen, btn_bg, btn_rect, border_radius=4)
            pygame.draw.rect(self.screen, COLOR_INK, btn_rect, 1, border_radius=4)
            btn_text = "Selected" if is_selected else "Select"
            bt = self.font_small.render(btn_text, True,
                                        (35, 30, 25) if is_selected else COLOR_INK)
            self.screen.blit(bt, (btn_rect.centerx - bt.get_width() // 2,
                                  btn_rect.centery - bt.get_height() // 2))
            buttons.append((btn_rect, f"select_{char_name}"))

        # Play button (card style)
        if len(selected_characters) >= num_players:
            play_rect = pygame.Rect(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 70, 160, 45)
            play_hover = play_rect.collidepoint(mouse_pos)
            bg = COLOR_PARCHMENT_DARK if play_hover else COLOR_PARCHMENT
            pygame.draw.rect(self.screen, COLOR_CARD_EDGE,
                             pygame.Rect(play_rect.x - 2, play_rect.y - 2, 164, 49),
                             border_radius=8)
            pygame.draw.rect(self.screen, bg, play_rect, border_radius=6)
            pygame.draw.rect(self.screen, COLOR_UI_HIGHLIGHT, play_rect, 2, border_radius=6)
            pt = self.font_medium.render(STRINGS["play"], True, COLOR_INK)
            self.screen.blit(pt, (play_rect.centerx - pt.get_width() // 2,
                                  play_rect.centery - pt.get_height() // 2))
            buttons.append((play_rect, "play"))

        # Back button (card style)
        back_rect = pygame.Rect(20, SCREEN_HEIGHT - 60, 80, 35)
        pygame.draw.rect(self.screen, COLOR_PARCHMENT_DARK, back_rect, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_INK, back_rect, 1, border_radius=4)
        bt = self.font_small.render(STRINGS["back"], True, COLOR_INK)
        self.screen.blit(bt, (back_rect.centerx - bt.get_width() // 2,
                              back_rect.centery - bt.get_height() // 2))
        buttons.append((back_rect, "back"))

        return buttons

    def render_game_over(self, won, score=None):
        """Render game over screen as a score card on the table."""
        self._draw_table_background()

        if won:
            text = STRINGS["game_over_win"]
            color = (180, 140, 20)
        else:
            text = STRINGS["game_over_lose"]
            color = (180, 50, 50)

        # Score card panel
        card_w, card_h = 400, 380
        card_x = SCREEN_WIDTH // 2 - card_w // 2
        card_y = 100
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        self._draw_card_panel(card_rect, radius=12)

        # Inner border
        inner = pygame.Rect(card_x + 10, card_y + 10, card_w - 20, card_h - 20)
        pygame.draw.rect(self.screen, COLOR_INK_LIGHT, inner, 1, border_radius=8)

        title = self.font_title.render(text, True, color)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2,
                                  card_y + 25))

        # Decorative line
        pygame.draw.line(self.screen, COLOR_INK,
                         (card_x + 40, card_y + 80), (card_x + card_w - 40, card_y + 80), 2)

        # Score breakdown
        if score:
            score_y = card_y + 95
            score_lines = [
                f"Level: {score['max_level']}",
                f"Monsters Slain: {score['kills']}",
                f"Gold Collected: {score['gold']}",
                f"Rounds Survived: {score['rounds']}",
            ]
            for i, line in enumerate(score_lines):
                line_surf = self.font_medium.render(line, True, COLOR_INK)
                self.screen.blit(line_surf,
                                 (SCREEN_WIDTH // 2 - line_surf.get_width() // 2,
                                  score_y + 10 + i * 35))
            btn_y = card_y + card_h - 60
        else:
            btn_y = card_y + card_h - 60

        # Menu button (card style)
        buttons = []
        rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, btn_y, 200, 45)
        mouse_pos = pygame.mouse.get_pos()
        bg = COLOR_PARCHMENT_DARK if rect.collidepoint(mouse_pos) else COLOR_PARCHMENT
        pygame.draw.rect(self.screen, COLOR_CARD_EDGE,
                         pygame.Rect(rect.x - 2, rect.y - 2, 204, 49),
                         border_radius=8)
        pygame.draw.rect(self.screen, bg, rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_INK, rect, 2, border_radius=6)
        text = self.font_medium.render("Main Menu", True, COLOR_INK)
        self.screen.blit(text, (rect.centerx - text.get_width() // 2,
                                rect.centery - text.get_height() // 2))
        buttons.append((rect, "menu"))

        return buttons

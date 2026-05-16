"""Mini Dungeon - Main Entry Point"""

import sys
import os

# Ensure src directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, CARD_COLS, CARD_ROWS,
    STATE_MENU, STATE_MODE_SELECT, STATE_CHAR_SELECT, STATE_PLAYING,
    STATE_GAME_OVER, CHARACTERS, TILE_SIZE, HUD_PANEL_HEIGHT
)
from world import WorldMap
from entities import Player
from game_logic import GameLogic
from renderer import Renderer


class Game:
    """Main game class managing state and input."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)

        self.state = STATE_MENU
        self.running = True

        # Character select state
        self.num_players = 1
        self.selected_characters = []

        # Game state
        self.world = None
        self.players = []
        self.game_logic = None

        # Monster turn animation timer
        self.monster_turn_timer = 0
        self.monster_turn_delay = 400  # ms between monster actions

        # Camera pan state
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.camera_dragging = False
        self.drag_start = None
        self.drag_offset_start = None

        # Skill targeting
        self.armed_skill = None  # None or skill_index (0 or 1)

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS)
            self._handle_events()
            self._update(dt)
            self._render()
            pygame.display.flip()

        pygame.quit()

    def _handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                # Right-click: start camera drag
                self.camera_dragging = True
                self.drag_start = event.pos
                self.drag_offset_start = (self.camera_offset_x, self.camera_offset_y)
            elif event.type == pygame.MOUSEMOTION and self.camera_dragging:
                # Update camera offset (inverted for grab-pan feel)
                dx = event.pos[0] - self.drag_start[0]
                dy = event.pos[1] - self.drag_start[1]
                self.camera_offset_x = self.drag_offset_start[0] - dx
                self.camera_offset_y = self.drag_offset_start[1] - dy
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self.camera_dragging = False
            elif event.type == pygame.MOUSEWHEEL:
                self.camera_offset_y -= event.y * TILE_SIZE
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_click(self, pos):
        """Handle mouse click based on current state."""
        if self.state == STATE_MENU:
            self._handle_menu_click(pos)
        elif self.state == STATE_MODE_SELECT:
            self._handle_mode_select_click(pos)
        elif self.state == STATE_CHAR_SELECT:
            self._handle_char_select_click(pos)
        elif self.state == STATE_PLAYING:
            self._handle_game_click(pos)
        elif self.state == STATE_GAME_OVER:
            self._handle_game_over_click(pos)

    def _handle_key(self, key):
        """Handle keyboard input."""
        if key == pygame.K_ESCAPE:
            if self.state == STATE_PLAYING:
                if self.armed_skill is not None:
                    self.armed_skill = None
                else:
                    self.state = STATE_MENU
            elif self.state == STATE_CHAR_SELECT:
                self.state = STATE_MODE_SELECT
            elif self.state == STATE_MODE_SELECT:
                self.state = STATE_MENU
            else:
                self.running = False
        elif key == pygame.K_SPACE and self.state == STATE_PLAYING:
            self.camera_offset_x = 0
            self.camera_offset_y = 0
        elif key == pygame.K_h and self.state == STATE_PLAYING:
            if self.game_logic and self.game_logic.is_player_phase:
                player = self.game_logic.get_current_player()
                if player:
                    if self.game_logic.player_use_potion(player):
                        self.game_logic.try_advance_turn()
        elif key == pygame.K_1 and self.state == STATE_PLAYING:
            self._arm_skill(0)
        elif key == pygame.K_2 and self.state == STATE_PLAYING:
            self._arm_skill(1)

    def _arm_skill(self, skill_index):
        """Arm a skill for targeting."""
        if not self.game_logic or not self.game_logic.is_player_phase:
            return
        player = self.game_logic.get_current_player()
        if not player or not player.can_use_skill(skill_index):
            return
        skill = player.skills[skill_index]
        # Self-target skills execute immediately
        if skill["target"] == "self":
            if self.game_logic.use_skill(player, skill_index):
                self.armed_skill = None
                self.game_logic.try_advance_turn()
            return
        # All-in-range skills execute immediately
        if skill["target"] == "all_in_range":
            if self.game_logic.use_skill(player, skill_index):
                self.armed_skill = None
                self.game_logic.try_advance_turn()
            return
        # Skills that need targeting
        self.armed_skill = skill_index

    def _handle_menu_click(self, pos):
        """Handle clicks on main menu."""
        buttons = self.renderer.render_menu()
        for rect, action in buttons:
            if rect.collidepoint(pos):
                if action == "start":
                    self.state = STATE_MODE_SELECT
                elif action == "quit":
                    self.running = False

    def _handle_mode_select_click(self, pos):
        """Handle clicks on game mode selection."""
        buttons = self.renderer.render_mode_select()
        for rect, action in buttons:
            if rect.collidepoint(pos):
                if action == "single":
                    self.num_players = 1
                    self.selected_characters = []
                    self.state = STATE_CHAR_SELECT
                elif action == "multi":
                    self.num_players = 2
                    self.selected_characters = []
                    self.state = STATE_CHAR_SELECT
                elif action == "back":
                    self.state = STATE_MENU

    def _handle_char_select_click(self, pos):
        """Handle clicks on character selection."""
        buttons = self.renderer.render_character_select(
            self.num_players, self.selected_characters)
        for rect, action in buttons:
            if rect.collidepoint(pos):
                if action.startswith("players_"):
                    self.num_players = int(action.split("_")[1])
                    # Reset selections if we reduced player count
                    while len(self.selected_characters) > self.num_players:
                        self.selected_characters.pop()
                elif action.startswith("select_"):
                    char_name = action[7:]  # Remove "select_"
                    if char_name in self.selected_characters:
                        self.selected_characters.remove(char_name)
                    elif len(self.selected_characters) < self.num_players:
                        self.selected_characters.append(char_name)
                elif action == "play":
                    self._start_game()
                elif action == "back":
                    self.state = STATE_MENU

    def _handle_game_click(self, pos):
        """Handle clicks during gameplay."""
        if not self.game_logic or self.game_logic.is_monster_phase:
            return
        if self.game_logic.game_over:
            return

        # Check skip button first
        buttons = self.renderer.render_skip_button(self.game_logic)
        for rect, action in buttons:
            if rect.collidepoint(pos):
                if action == "skip":
                    self.game_logic.player_skip()
                    self.armed_skill = None
                return

        # Check skill buttons
        skill_buttons = self.renderer.render_skill_buttons(self.game_logic)
        for rect, action in skill_buttons:
            if rect.collidepoint(pos):
                if action.startswith("skill_"):
                    idx = int(action.split("_")[1])
                    self._arm_skill(idx)
                return

        # Click on game world (only in map area, above HUD)
        if pos[1] < SCREEN_HEIGHT - HUD_PANEL_HEIGHT:
            player = self.game_logic.get_current_player()
            if not player or player.action_points <= 0:
                return

            world_row, world_col = self.renderer.camera.screen_to_world(pos[0], pos[1])

            # If a skill is armed, use it on the clicked target
            if self.armed_skill is not None:
                success = self.game_logic.use_skill(
                    player, self.armed_skill, world_row, world_col)
                if success:
                    self.armed_skill = None
                    self.game_logic.try_advance_turn()
                return

            # Normal contextual click
            targets = self._get_contextual_targets(player)

            # Priority: attack → door → chest → move
            success = False
            if (world_row, world_col) in targets["attack"]:
                success = self.game_logic.player_attack(player, world_row, world_col)
            elif (world_row, world_col) in targets["door"]:
                success = self.game_logic.player_open_door(player, world_row, world_col)
            elif (world_row, world_col) in targets["chest"]:
                success = self.game_logic.player_open_chest(player, world_row, world_col)
            elif (world_row, world_col) in targets["move"]:
                success = self.game_logic.player_move(player, world_row, world_col)

            if success:
                self.game_logic.try_advance_turn()

    def _handle_game_over_click(self, pos):
        """Handle clicks on game over screen."""
        score = self.game_logic.get_score_summary()
        buttons = self.renderer.render_game_over(self.game_logic.game_won, score)
        for rect, action in buttons:
            if rect.collidepoint(pos):
                if action == "menu":
                    self.state = STATE_MENU

    def _get_contextual_targets(self, player):
        """Get all interactable tiles grouped by action type."""
        targets = {"move": [], "attack": [], "door": [], "chest": [], "skill": []}
        if not player or player.action_points <= 0:
            return targets

        # If a skill is armed, show skill-specific targets
        if self.armed_skill is not None and self.armed_skill < len(player.skills):
            skill = player.skills[self.armed_skill]
            if skill["target"] == "melee":
                monsters = self.game_logic.get_adjacent_monsters(player)
                skill_tiles = []
                for m in monsters:
                    skill_tiles.extend(m.get_occupied_tiles())
                targets["skill"] = skill_tiles
            elif skill["target"] == "ranged":
                r = skill.get("range", 3)
                for dr in range(-r, r + 1):
                    for dc in range(-r, r + 1):
                        if 1 <= abs(dr) + abs(dc) <= r:
                            targets["skill"].append((player.world_row + dr, player.world_col + dc))
            elif skill["target"] == "adjacent_tile":
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = player.world_row + dr, player.world_col + dc
                    if self.game_logic.world.is_walkable(nr, nc):
                        if not self.game_logic.world.get_monster_at(nr, nc):
                            targets["skill"].append((nr, nc))
            return targets

        # Normal targets
        monsters = self.game_logic.get_attackable_monsters(player)
        attack_tiles = []
        for m in monsters:
            attack_tiles.extend(m.get_occupied_tiles())
        targets["attack"] = attack_tiles
        targets["door"] = self.game_logic.get_adjacent_doors(player)
        targets["chest"] = self.game_logic.get_adjacent_chests(player)
        targets["move"] = self.game_logic.get_valid_move_tiles(player)
        return targets

    def _start_game(self):
        """Initialize a new game."""
        self.world = WorldMap()
        self.players = []

        # Create players
        # Place players at center of first card
        start_row = CARD_ROWS // 2
        start_col = CARD_COLS // 2

        for i, char_name in enumerate(self.selected_characters):
            player = Player(i, char_name)
            player.world_row = start_row
            player.world_col = start_col + i  # Offset each player
            self.players.append(player)

        # Remove any monster at player start positions
        player_positions = set((p.world_row, p.world_col) for p in self.players)
        self.world.monsters = [
            m for m in self.world.monsters
            if (m.world_row, m.world_col) not in player_positions
        ]

        self.game_logic = GameLogic(self.world, self.players)
        self.state = STATE_PLAYING

    def _update(self, dt):
        """Update game state."""
        if self.state != STATE_PLAYING or not self.game_logic:
            return

        # Check game over
        if self.game_logic.game_over:
            self.state = STATE_GAME_OVER
            return

        # Process monster turns with delay
        if self.game_logic.is_monster_phase:
            self.monster_turn_timer += dt
            if self.monster_turn_timer >= self.monster_turn_delay:
                self.monster_turn_timer = 0
                self.game_logic.process_monster_turn()

    def _render(self):
        """Render current state."""
        if self.state == STATE_MENU:
            self.renderer.render_menu()
        elif self.state == STATE_MODE_SELECT:
            self.renderer.render_mode_select()
        elif self.state == STATE_CHAR_SELECT:
            self.renderer.render_character_select(
                self.num_players, self.selected_characters)
        elif self.state == STATE_PLAYING:
            # Compute contextual highlights
            highlights = {"move": [], "attack": [], "door": [], "chest": [], "skill": []}
            player = self.game_logic.get_current_player()
            if player and player.action_points > 0:
                highlights = self._get_contextual_targets(player)
            self.renderer.render_game(
                self.world, self.players, self.game_logic, highlights,
                camera_offset=(self.camera_offset_x, self.camera_offset_y))
            self.renderer.render_skip_button(self.game_logic)
            self.renderer.render_skill_buttons(self.game_logic)
            # Skill armed hint
            if self.armed_skill is not None and self.game_logic:
                player = self.game_logic.get_current_player()
                if player and self.armed_skill < len(player.skills):
                    skill = player.skills[self.armed_skill]
                    hint = f"{skill['name']} armed — click target. Esc to cancel."
                    self.renderer.draw_skill_hint(hint)
        elif self.state == STATE_GAME_OVER:
            score = self.game_logic.get_score_summary()
            self.renderer.render_game_over(self.game_logic.game_won, score)


if __name__ == "__main__":
    game = Game()
    game.run()

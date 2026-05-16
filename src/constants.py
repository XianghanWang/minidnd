"""Mini Dungeon - Game Constants and Configuration"""

# Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Mini Dungeon"

# Tile sizes
TILE_SIZE = 48

# Dungeon card dimensions (in tiles)
CARD_COLS = 7
CARD_ROWS = 5

# Boss room spans 3x3 card grid = 15 rows x 21 cols
BOSS_GRID_ROWS = 3
BOSS_GRID_COLS = 3

# Colors (Micro Dungeon PnP style - black table, white cards, bold ink)
COLOR_BG = (15, 12, 10)              # Near-black void
COLOR_TABLE = (20, 18, 15)           # Pure black table
COLOR_TABLE_DARK = (12, 10, 8)       # Table shadow
COLOR_TABLE_LIGHT = (30, 25, 20)     # Subtle table highlight
COLOR_CARD_EDGE = (200, 195, 185)    # Off-white card border
COLOR_CARD_SHADOW = (0, 0, 0, 160)   # Deep card drop shadow
COLOR_CARD_FILL = (240, 235, 225)    # White card interior
COLOR_ROAD = (235, 230, 218)         # White floor (card surface)
COLOR_WALL = (45, 40, 35)            # Near-black wall (bold ink)
COLOR_WALL_HATCH = (65, 58, 50)      # Cross-hatch accent
COLOR_DOOR = (160, 130, 70)          # Wooden door
COLOR_DOOR_LOCKED = (130, 100, 50)   # Darker locked door
COLOR_CHEST = (210, 175, 50)         # Treasure gold
COLOR_PLAYER = (50, 130, 200)        # Player blue token
COLOR_MONSTER = (200, 45, 45)        # Monster red
COLOR_BOSS = (160, 30, 160)          # Boss purple
COLOR_INK = (25, 20, 15)             # Bold black ink
COLOR_INK_LIGHT = (100, 90, 75)      # Light ink for details
COLOR_UI_BG = (25, 22, 18)           # Near-black panel
COLOR_UI_TEXT = (235, 230, 218)       # White text
COLOR_UI_HIGHLIGHT = (240, 190, 60)  # Gold highlight
COLOR_UI_BUTTON = (50, 45, 38)       # Dark button
COLOR_UI_BUTTON_HOVER = (75, 65, 52) # Button hover
COLOR_HEALTH_BAR = (190, 40, 40)     # Red health
COLOR_HEALTH_BG = (70, 55, 55)       # Health bg
COLOR_AP_BAR = (50, 160, 50)         # Green AP
COLOR_GRID_LINE = (195, 190, 178)    # Subtle grid on white card
COLOR_PARCHMENT = (240, 235, 225)    # White card surface
COLOR_PARCHMENT_DARK = (220, 212, 198)  # Slightly aged card

# Character definitions
CHARACTERS = {
    "Warrior": {
        "attack": 3,
        "health": 10,
        "max_health": 10,
        "action_points": 3,
        "speed": 2,
        "attack_range": 1,
        "description": "Strong and tough. A frontline fighter.",
        "color": (100, 140, 200),
    },
    "Wizard": {
        "attack": 5,
        "health": 6,
        "max_health": 6,
        "action_points": 2,
        "speed": 1,
        "attack_range": 1,
        "description": "Powerful spells but fragile.",
        "color": (160, 80, 200),
    },
    "Hunter": {
        "attack": 4,
        "health": 7,
        "max_health": 7,
        "action_points": 3,
        "speed": 3,
        "attack_range": 3,
        "description": "Fast and versatile. Strikes swiftly.",
        "color": (80, 180, 80),
    },
}

# Skill definitions per character class
SKILLS = {
    "Warrior": [
        {
            "name": "Shield Bash",
            "description": "Stun a monster for 1 turn",
            "ap_cost": 1,
            "cooldown": 3,
            "damage": 2,
            "target": "melee",
            "effect": "stun",
            "stun_turns": 1,
            "key": "1",
        },
        {
            "name": "War Cry",
            "description": "+2 ATK for 2 turns",
            "ap_cost": 1,
            "cooldown": 4,
            "damage": 0,
            "target": "self",
            "effect": "buff_attack",
            "buff_amount": 2,
            "buff_turns": 2,
            "key": "2",
        },
    ],
    "Wizard": [
        {
            "name": "Fireball",
            "description": "AoE: 4 dmg to target, 2 splash",
            "ap_cost": 2,
            "cooldown": 4,
            "damage": 4,
            "splash_damage": 2,
            "splash_range": 1,
            "target": "ranged",
            "range": 3,
            "effect": "aoe",
            "key": "1",
        },
        {
            "name": "Heal",
            "description": "Heal self for 6 HP",
            "ap_cost": 1,
            "cooldown": 3,
            "damage": 0,
            "target": "self",
            "effect": "heal",
            "heal_amount": 6,
            "key": "2",
        },
    ],
    "Hunter": [
        {
            "name": "Multi-Shot",
            "description": "Hit ALL monsters in range for 3 dmg",
            "ap_cost": 2,
            "cooldown": 3,
            "damage": 3,
            "target": "all_in_range",
            "effect": "multi_hit",
            "key": "1",
        },
        {
            "name": "Trap",
            "description": "Place trap on adjacent tile (5 dmg)",
            "ap_cost": 1,
            "cooldown": 4,
            "damage": 5,
            "target": "adjacent_tile",
            "effect": "trap",
            "key": "2",
        },
    ],
    "Boss": [
        {
            "name": "Dark Bolt",
            "description": "Ranged dark energy bolt (8 dmg, range 4)",
            "damage": 8,
            "target": "ranged",
            "range": 4,
            "cooldown": 2,
            "effect": "damage",
        },
        {
            "name": "Stomp",
            "description": "AoE shockwave: 5 dmg to all adjacent",
            "damage": 5,
            "target": "aoe_around_self",
            "range": 2,
            "cooldown": 3,
            "effect": "aoe_self",
        },
        {
            "name": "Summon",
            "description": "Summon a skeleton minion",
            "damage": 0,
            "target": "self",
            "cooldown": 5,
            "effect": "summon",
            "summon_type": "Skeleton",
        },
    ],
}
MONSTERS = {
    "Goblin": {
        "attack": 2,
        "health": 6,
        "speed": 2,
        "color": (100, 180, 60),
        "territory": 4,
        "xp": 8,
        "action_points": 2,
    },
    "Skeleton": {
        "attack": 3,
        "health": 8,
        "speed": 1,
        "color": (220, 220, 200),
        "territory": 3,
        "xp": 12,
        "action_points": 1,
    },
    "Orc": {
        "attack": 4,
        "health": 12,
        "speed": 1,
        "color": (60, 120, 60),
        "territory": 5,
        "xp": 20,
        "action_points": 2,
    },
    "Bat": {
        "attack": 1,
        "health": 4,
        "speed": 3,
        "color": (80, 60, 100),
        "territory": 5,
        "xp": 5,
        "action_points": 2,
    },
    "Slime": {
        "attack": 2,
        "health": 10,
        "speed": 1,
        "color": (60, 200, 100),
        "territory": 3,
        "xp": 10,
        "action_points": 1,
    },
    "Spider": {
        "attack": 3,
        "health": 7,
        "speed": 2,
        "color": (70, 50, 50),
        "territory": 4,
        "xp": 15,
        "action_points": 2,
    },
    "Wraith": {
        "attack": 5,
        "health": 9,
        "speed": 2,
        "color": (140, 140, 180),
        "territory": 5,
        "xp": 25,
        "action_points": 2,
    },
    "Boss": {
        "attack": 10,
        "health": 80,
        "speed": 1,
        "color": (180, 30, 180),
        "territory": 12,
        "xp": 0,
        "action_points": 4,
        "size": 2,  # 2x2 tiles
        "attack_range": 3,
    },
}

# Item definitions
ITEMS = {
    "Sword": {"type": "weapon", "attack_bonus": 2, "description": "+2 Attack"},
    "Staff": {"type": "weapon", "attack_bonus": 3, "description": "+3 Attack"},
    "Dagger": {"type": "weapon", "attack_bonus": 1, "description": "+1 Attack"},
    "Bow": {"type": "weapon", "attack_bonus": 1, "attack_range": 3, "description": "+1 ATK, Range 3"},
    "Long Bow": {"type": "weapon", "attack_bonus": 2, "attack_range": 5, "description": "+2 ATK, Range 5"},
    "Health Potion": {"type": "potion", "heal": 3, "description": "Restore 3 HP"},
    "Greater Potion": {"type": "potion", "heal": 5, "description": "Restore 5 HP"},
    "Key": {"type": "key", "description": "Opens a locked door"},
    "Gold": {"type": "treasure", "value": 10, "description": "10 Gold"},
    "Gem": {"type": "treasure", "value": 25, "description": "25 Gold"},
}

# Loot table weights (item_name: weight)
LOOT_TABLE = {
    "Sword": 10,
    "Staff": 5,
    "Dagger": 15,
    "Health Potion": 25,
    "Greater Potion": 10,
    "Key": 15,
    "Gold": 15,
    "Gem": 5,
    "Bow": 10,
    "Long Bow": 3,
}

# UI layout
HUD_PANEL_HEIGHT = 140

# Game rules
BOSS_CARD_THRESHOLD = 8  # Boss card appears after this many cards drawn
MONSTER_BUFF_INTERVAL = 5  # Monsters get buffed every N rounds
MAX_PLAYERS = 4

# Tile types
TILE_ROAD = 0
TILE_WALL = 1
TILE_DOOR = 2
TILE_DOOR_LOCKED = 3
TILE_CHEST = 4

# Game states
STATE_MENU = "menu"
STATE_MODE_SELECT = "mode_select"
STATE_CHAR_SELECT = "char_select"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

# Action types
ACTION_MOVE = "move"
ACTION_ATTACK = "attack"
ACTION_OPEN_DOOR = "open_door"
ACTION_OPEN_CHEST = "open_chest"
ACTION_SKIP = "skip"

# Localization (English - designed for future expansion)
STRINGS = {
    "title": "Mini Dungeon",
    "start_game": "Start Game",
    "select_character": "Select Your Character",
    "player_turn": "Player {}'s Turn",
    "monster_turn": "Monster Turn",
    "action_points": "AP: {}/{}",
    "health": "HP: {}/{}",
    "attack": "ATK: {}",
    "speed": "SPD: {}",
    "round": "Round {}",
    "game_over_win": "Victory! The Boss is defeated!",
    "game_over_lose": "Defeat! You have fallen...",
    "move": "Move",
    "attack_action": "Attack",
    "open_door": "Open Door",
    "open_chest": "Open Chest",
    "skip_turn": "Skip Turn",
    "players": "Players: {}",
    "back": "Back",
    "play": "Play",
    "quit": "Quit",
    "inventory": "Inventory",
    "gold": "Gold: {}",
    "cards_drawn": "Cards: {}/{}",
}

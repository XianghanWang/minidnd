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

# Colors (hand-drawn ink-on-parchment style - like a pen sketch)
COLOR_BG = (35, 30, 28)              # Dark dungeon void (unexplored)
COLOR_TABLE = (90, 65, 40)           # Wood table base
COLOR_TABLE_DARK = (70, 50, 30)      # Wood grain line
COLOR_TABLE_LIGHT = (110, 80, 50)    # Wood grain highlight
COLOR_CARD_EDGE = (220, 210, 190)    # Card border/edge cream
COLOR_CARD_SHADOW = (30, 25, 20, 120)  # Card drop shadow
COLOR_ROAD = (70, 65, 55)            # Dark stone floor
COLOR_WALL = (40, 35, 30)            # Very dark dungeon wall
COLOR_WALL_HATCH = (55, 50, 42)      # Subtle brick pattern on walls
COLOR_DOOR = (160, 130, 80)          # Wooden door brown
COLOR_DOOR_LOCKED = (120, 90, 50)    # Darker locked door
COLOR_CHEST = (180, 150, 60)         # Treasure gold-ish
COLOR_PLAYER = (60, 160, 220)        # Player pawns stay colorful
COLOR_MONSTER = (200, 50, 50)        # Monster accent
COLOR_BOSS = (180, 30, 180)          # Boss accent
COLOR_INK = (35, 30, 25)             # Primary ink color
COLOR_INK_LIGHT = (120, 110, 90)     # Lighter ink for details
COLOR_UI_BG = (35, 30, 25)           # Dark panel
COLOR_UI_TEXT = (240, 230, 210)       # Cream text on dark
COLOR_UI_HIGHLIGHT = (255, 200, 80)   # Gold highlight
COLOR_UI_BUTTON = (60, 50, 40)        # Button bg
COLOR_UI_BUTTON_HOVER = (90, 75, 55)  # Button hover
COLOR_HEALTH_BAR = (180, 40, 40)      # Red health
COLOR_HEALTH_BG = (80, 60, 60)        # Health bg
COLOR_AP_BAR = (50, 160, 50)          # Green AP
COLOR_GRID_LINE = (60, 55, 45)       # Subtle grid on stone
COLOR_PARCHMENT = (235, 225, 200)    # Light parchment
COLOR_PARCHMENT_DARK = (210, 195, 170)  # Darker parchment

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
}

# Monster definitions
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
        "attack": 8,
        "health": 60,
        "speed": 1,
        "color": (180, 30, 180),
        "territory": 8,
        "xp": 0,
        "action_points": 3,
        "size": 2,  # 2x2 tiles
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

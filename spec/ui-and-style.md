# UI and Visual Style

## Art Direction
- **Micro Dungeon PnP card game style**
- Inspired by [Micro Dungeon](https://boardgamegeek.com/boardgame/332306/micro-dungeon) board game
- Bold black ink illustrations on white cards, laid on a pure black table
- No external art assets — all visuals drawn with Pygame primitives

## Color Palette
- **Table**: Near-black (20, 18, 15) — pure dark table surface
- **Card fill**: White/cream (240, 235, 225)
- **Ink (primary)**: Bold near-black (25, 20, 15)
- **Ink (light)**: For details (100, 90, 75)
- **Walls**: Dark ink fill (45, 40, 35)
- **Floors**: White card surface (235, 230, 218)
- **Grid lines**: Subtle on white (195, 190, 178)
- **Player tokens**: Colored circles (blue, purple, green) with class icons
- **UI panels**: White card on black table

## Card Borders
- **Torn/rough edges**: Irregular polygon with jittered vertices (not clean rectangles)
- **Fuzzy paper fibers**: Tiny lines radiating outward from card edges
- **Bold ink inner border**: 2px black line inside the torn edge
- **Deep drop shadow**: Black shadow on dark table for depth
- **Light aging marks**: Subtle semi-transparent circles for used card look
- **Corner ink dots**: Decorative dots at all four corners

## Tile Rendering
- Walls: Dark ink fill, flat style
- Doors: Wooden plank style with ink outline and handle
- Locked doors: Darker shade + lock icon
- Chests: Hand-drawn box with lid arc and latch (gold accent)
- Road: White/cream with subtle floor variants

## Player Appearance
- **Circular tokens** (radius 16) with class icons drawn in cream/white:
  - Warrior: Crossed swords
  - Wizard: 5-pointed star
  - Hunter: Bow and arrow
- Bottom-half darker arc for depth
- Elliptical shadow underneath
- Current player: Golden pulsing ring

## Monster Appearance
- Per-type ink illustrations (Goblin, Skeleton, Orc, Spider, etc.)
- Sleeping monsters: Semi-transparent with bobbing "zzz" text
- Chasing monsters: Red exclamation mark
- Boss: 2×2 tiles, large detailed illustration
- Health bars with ink-outlined thin bars above each monster

## Character Card HUD (Bottom Panel)
The bottom HUD is styled as a Micro Dungeon character card:
- **Character portrait**: Ink-sketch illustration on the left (Warrior with sword/shield, Wizard with staff/hat, Hunter with bow)
- **Name and level**: Title text with underline, level badge in top-right corner
- **Stat grid**: ATK (sword icon), Speed (boot icon), Range (arrow icon) with numbers
- **HP bar**: Red translucent cubes (segmented, like board game dice)
- **AP pips**: Green translucent cubes
- **XP indicator**: Small text showing progress to next level
- **Inventory row**: Key, gold, potion, weapon icons with counts
- **Info card**: Separate small card showing Round number, Cards drawn, Kills

## Message Log
- Floating above HUD panel (not inside it)
- Semi-transparent dark background
- Last 4 messages with fade effect (newer = brighter)

## Screen Layout
- **Resolution**: 1280×720
- **Tile size**: 48×48 pixels
- **Bottom panel** (160px): Character card HUD + info card
- **Top-center**: Phase indicator banner (card-style tag)
- **Above HUD**: Floating message log (right side)
- **Background**: Pure black table with subtle noise texture

## Screens
1. Main Menu (title + start/quit)
2. Mode Select (single/multiplayer)
3. Character Select (pick characters, set player count)
4. Game (dungeon view + character card HUD)
5. Game Over (win/lose message + score breakdown + return to menu)

## Animations
- Monster claw attack: Three diagonal scratch marks
- Fireball explosion: Expanding orange/red flash
- Trap trigger: Red flash on tile
- Level up: Golden expanding ring
- Damage flash: Red tint on damaged entities
- Ambient dust particles (screen-space)

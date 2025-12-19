# Sea Battle

This project is a simplified version of the classic **Battleship** game, playable entirely through the terminal.

The game strictly follows the required rules, including ship placement validation, continuous game state tracking, and an intelligent bot opponent.

The architecture is designed to be **storage-agnostic** and **UI-agnostic**, so the core game logic does not depend on how data is stored or displayed.

---

## Ship Configuration and Rules

Each player has the following fleet:

- 1 ship of size **4**
- 2 ships of size **3**
- 3 ships of size **2**
- 4 ships of size **1**

### Placement rules

- All ships are placed on a **10×10 board**
- Ships must be placed **horizontally or vertically**
- Ships must be **contiguous**
- Ships **must not touch each other**, even **diagonally**
- Ships must not overlap
- Ships must not go outside the board

---

## Project Structure

.
├─ main.py  
├─ data/  
│  ├─ player_ships.csv  
│  ├─ bot_ships.csv  
│  └─ game_state.csv  
├─ outputs/  
├─ src/  
│  ├─ domain.py  
│  ├─ gameplay.py  
│  ├─ engine/  
│  │  ├─ game_manager.py  
│  │  └─ bot_brain.py  
│  ├─ storage/  
│  │  ├─ interfaces.py  
│  │  └─ csv_storage.py  
│  ├─ ui/  
│  │  ├─ interfaces.py  
│  │  ├─ console_input.py  
│  │  └─ console_renderer.py  
│  └─ validators/  
│     └─ fleet_validator.py  
├─ requirements.txt  
└─ README.md  

---

## How Player Input Works

The **player ship layout is loaded from a CSV file**, not from console input.

### Player ships file

File: `data/player_ships.csv`

Format:

ship_id,row,col

- `ship_id` — identifier of a ship
- `row`, `col` — zero-based coordinates (`0..9`)
- Each ship is represented by multiple rows
- Single-cell ships appear once

Before the game starts, this file is:

1. Loaded using a `FleetRepository`
2. Fully validated
3. Rejected with an error if invalid

---

## Ship Placement Validation

Validation is implemented in:

`src/validators/fleet_validator.py`

The validator checks:

- Correct ship sizes: `4,3,3,2,2,2,1,1,1,1`
- All ship cells are inside the board
- Ships are straight and contiguous
- No overlapping cells
- No touching ships (including all 8 neighboring directions)

If validation fails, the game stops with a clear error message.

---

## Bot Ship Generation

The bot fleet is generated automatically.

Implementation:

`src/placement/bot_setup.py`

The generator:

- Randomly places ships
- Respects all placement rules
- Prevents overlap and diagonal touching
- Saves the result to `data/bot_ships.csv`

This ensures compatibility between player and bot fleets.

---

## Game State Tracking

All gameplay progress is continuously saved to:

`data/game_state.csv`

### Stored per turn

Each row contains:

- Turn number
- Player move (coordinate)
- Player result (`hit`, `miss`, `sunk`)
- Bot move (coordinate)
- Bot result (`hit`, `miss`, `sunk`)
- Player fog-of-war board (100 characters)
- Bot fog-of-war board (100 characters)

### Board encoding

Each board is encoded as **100 characters**, row by row:

- `?` — unknown cell
- `o` — miss
- `x` — hit or sunk

This encoding allows full game restoration from CSV.

---

## Displaying the Game State

After **every turn**, the game state is:

- Written to `game_state.csv`
- Rendered in the terminal as two boards:
  - **Player board** (ships visible)
  - **Enemy board** (fog-of-war)

Rendering is handled by:

`src/ui/console_renderer.py`

The rendering logic is fully isolated from game logic and storage.

---

## Destroyed Ships and Automatic Miss Marking

When a ship is **fully destroyed**:

- All surrounding cells (8 directions) are automatically marked as **miss**
- These marks are:
  - Reflected in the in-memory game state
  - Written to `game_state.csv`
  - Displayed in the terminal

This behavior is implemented in the `GameManager`.

---

## Gameplay Loop

The main gameplay loop is implemented in:

`src/gameplay.py`

The loop performs the following steps:

1. Render the current state
2. Read player input (shot coordinate)
3. Apply player move
4. Apply bot move
5. Update the game state
6. Save the turn to CSV
7. Render the updated state

The game ends when one side has **no ships remaining**.

---

## Bot Move Logic

The bot follows an intelligent strategy:

### 1. Random shooting
- Shoots random untested cells initially

### 2. Smart follow-up after first hit
- After a hit, checks adjacent cells (up, down, left, right)

### 3. Axis locking after second hit
- Determines ship orientation
- Continues shooting along that axis
- Stops at misses or board boundaries

### 4. Reset after ship destruction
- After a ship is sunk, the bot returns to random shooting

Bot logic is implemented in:

`src/engine/bot_brain.py`

---

## Architecture and Design Decisions

### MVC-like separation

- **Model**: `src/domain.py`
- **Game logic (Manager)**: `GameManager`
- **View**: `ConsoleRenderer`
- **Controller**: `gameplay.py`
- **Storage**: Repository interfaces + CSV implementation

### Storage abstraction

The game logic does **not depend on CSV** directly.

CSV is only one implementation of storage, which allows:

- Switching to another format (JSON, database)
- Replaying games from saved states
- Extending logging without touching game logic

---

## Running the Game (Poetry)

Requirements:

- Python **3.12**
- Poetry

Install dependencies:
```bash
poetry install
```

Run the game:
```bash
poetry run python main.py
```

If `player_ships.csv`, `bot_ships.csv`, and `game_state.csv` already exist, the game will offer to **resume** from the saved state.

---

## Notes

- The player fleet must exist in `data/player_ships.csv` before starting a new game
- All errors in ship placement are reported before the game starts
- The project intentionally avoids hard dependencies between logic, UI, and storage

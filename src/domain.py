from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

BOARD_SIZE = 10


@dataclass(frozen=True, order=True)
class Coordinate:
    row: int
    col: int

    def is_inside(self, size: int = BOARD_SIZE) -> bool:
        return 0 <= self.row < size and 0 <= self.col < size

    def neighbors_8(self) -> List["Coordinate"]:
        # 8-directional neighbors (including diagonals)
        result: List[Coordinate] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                result.append(Coordinate(self.row + dr, self.col + dc))
        return result

    def neighbors_4(self) -> List["Coordinate"]:
        # 4-directional neighbors (up, down, left, right)
        return [
            Coordinate(self.row - 1, self.col),
            Coordinate(self.row + 1, self.col),
            Coordinate(self.row, self.col - 1),
            Coordinate(self.row, self.col + 1),
        ]


class ShotOutcome(Enum):
    MISS = "miss"
    HIT = "hit"
    SUNK = "sunk"


class FogCell(Enum):
    UNKNOWN = "?"
    MISS = "o"
    HIT = "x"

# class FogSymbol(Enum):
#     UNKNOWN = "?"
#     MISS = "o"
#     HIT = "x"

@dataclass
class Ship:
    # Ship is represented by its occupied cells
    cells: List[Coordinate]

    @property
    def length(self) -> int:
        return len(self.cells)

    def cell_set(self) -> Set[Coordinate]:
        return set(self.cells)


@dataclass
class Fleet:
    ships: List[Ship]

    def occupied_cells(self) -> Set[Coordinate]:
        result: Set[Coordinate] = set()
        for ship in self.ships:
            result |= ship.cell_set()
        return result

    def find_ship_containing(self, cell: Coordinate) -> Optional[Ship]:
        for ship in self.ships:
            if cell in ship.cell_set():
                return ship
        return None


@dataclass
class FogBoard:
    """
    This board stores only the information discovered by shots:
    - miss/hit/sunk on specific cells
    Unknown cells are not stored.
    """
    size: int = BOARD_SIZE
    shots: Dict[Coordinate, ShotOutcome] = field(default_factory=dict)

    def has_been_shot(self, cell: Coordinate) -> bool:
        return cell in self.shots

    def set_miss(self, cell: Coordinate) -> None:
        if cell.is_inside(self.size) and cell not in self.shots:
            self.shots[cell] = ShotOutcome.MISS

    def set_hit(self, cell: Coordinate) -> None:
        if cell.is_inside(self.size):
            self.shots[cell] = ShotOutcome.HIT

    def set_sunk(self, cell: Coordinate) -> None:
        if cell.is_inside(self.size):
            self.shots[cell] = ShotOutcome.SUNK

    def symbol_at(self, cell: Coordinate) -> str:
        outcome = self.shots.get(cell)
        if outcome is None:
            return FogCell.UNKNOWN.value
        if outcome == ShotOutcome.MISS:
            return FogCell.MISS.value
        # HIT and SUNK are shown as the same symbol on the fog board
        return FogCell.HIT.value

    def encode_100(self) -> str:
        """
        100 chars: row-major order, symbols:
        '?' unknown, 'o' miss, 'x' hit/sunk
        """
        chars: List[str] = []
        for r in range(self.size):
            for c in range(self.size):
                chars.append(self.symbol_at(Coordinate(r, c)))
        return "".join(chars)
    
    @staticmethod
    def decode_100(encoded: str, size: int = BOARD_SIZE) -> "FogBoard":
        if len(encoded) != size * size:
            raise ValueError("Bad encoded board length")
        board = FogBoard(size=size)
        i = 0
        for r in range(size):
            for c in range(size):
                ch = encoded[i]
                i += 1
                cell = Coordinate(r, c)
                if ch == FogCell.MISS.value:
                    board.shots[cell] = ShotOutcome.MISS
                elif ch == FogCell.HIT.value:
                    board.shots[cell] = ShotOutcome.HIT
        return board


@dataclass
class Move:
    actor: str  # "player" or "bot"
    target: Coordinate
    outcome: ShotOutcome


@dataclass
class GameState:
    """
    Stores both fog-of-war boards and move history.
    - player_view: what the player knows about bot's board
    - bot_view: what the bot knows about player's board
    """
    turn_number: int = 0
    player_view: FogBoard = field(default_factory=FogBoard)
    bot_view: FogBoard = field(default_factory=FogBoard)
    # One entry per turn: (player_move, bot_move)
    turn_history: List[Tuple[Move, Move]] = field(default_factory=list)

    def advance_turn(self) -> None:
        self.turn_number += 1

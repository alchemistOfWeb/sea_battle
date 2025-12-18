import csv
from pathlib import Path
from typing import Dict, List

from src.domain import Coordinate, Ship, Fleet, GameState, Move, ShotOutcome, FogBoard
from src.storage.base import FleetRepository, GameStateRepository


class CsvFleetRepository(FleetRepository):
    """
    CSV format:
      ship_id,row,col
    Each ship is represented by multiple rows.
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def save(self, fleet: Fleet) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ship_id", "row", "col"])
            for ship_id, ship in enumerate(fleet.ships, start=1):
                for cell in ship.cells:
                    writer.writerow([ship_id, cell.row, cell.col])

    def load(self) -> Fleet:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Fleet file not found: {self.file_path}")

        cells_by_ship_id: Dict[int, List[Coordinate]] = {}

        with self.file_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ship_id = int(row["ship_id"])
                cell = Coordinate(int(row["row"]), int(row["col"]))
                cells_by_ship_id.setdefault(ship_id, []).append(cell)

        ships: List[Ship] = []
        for ship_id in sorted(cells_by_ship_id.keys()):
            ships.append(Ship(cells=cells_by_ship_id[ship_id]))

        return Fleet(ships=ships)


class CsvGameStateRepository(GameStateRepository):
    """
    CSV format:
      turn,
      player_move,player_result,
      bot_move,bot_result,
      player_view_100,bot_view_100

    - move format: "row,col"
    - boards are 100-char strings (row-major)
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def init_new(self, state: GameState) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "turn",
                "player_move", "player_result",
                "bot_move", "bot_result",
                "player_view_100",
                "bot_view_100",
            ])

    def append_turn(self, state: GameState) -> None:
        if not state.turn_history:
            raise ValueError("No turns in history to append.")

        player_move, bot_move = state.turn_history[-1]

        def format_move(move: Move) -> str:
            return f"{move.target.row},{move.target.col}"

        with self.file_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                state.turn_number,
                format_move(player_move), player_move.outcome.value,
                format_move(bot_move), bot_move.outcome.value,
                state.player_view.encode_100(),
                state.bot_view.encode_100(),
            ])

    def load(self) -> GameState:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Game state file not found: {self.file_path}")

        rows: List[dict] = []
        with self.file_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows.append(row)

        state = GameState()
        if not rows:
            return state

        for row in rows:
            turn = int(row["turn"])
            player_move = self._parse_move("player", row["player_move"], row["player_result"])
            bot_move = self._parse_move("bot", row["bot_move"], row["bot_result"])
            state.turn_history.append((player_move, bot_move))
            state.turn_number = turn
            state.player_view = FogBoard.decode_100(row["player_view_100"])
            state.bot_view = FogBoard.decode_100(row["bot_view_100"])

        return state

    @staticmethod
    def _parse_move(actor: str, move_str: str, outcome_str: str) -> Move:
        parts = move_str.split(",")
        if len(parts) != 2:
            raise ValueError(f"Bad move format: {move_str}")
        r = int(parts[0])
        c = int(parts[1])
        return Move(actor=actor, target=Coordinate(r, c), outcome=ShotOutcome(outcome_str))

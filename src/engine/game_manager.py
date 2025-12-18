from dataclasses import dataclass
from typing import Optional, Set

from src.domain import Coordinate, Fleet, GameState, Move, ShotOutcome, FogBoard
from src.engine.bot_brain import BotBrain


@dataclass
class GameResult:
    winner: Optional[str] = None  # "player", "bot", or None


class GameManager:
    """
    Pure game logic. No printing, no input reading, no CSV knowledge.
    """

    def __init__(self, player_fleet: Fleet, bot_fleet: Fleet, bot_brain: Optional[BotBrain] = None):
        self.player_fleet = player_fleet
        self.bot_fleet = bot_fleet

        self.state = GameState()
        self.player_hits_on_bot: Set[Coordinate] = set()
        self.bot_hits_on_player: Set[Coordinate] = set()

        self.bot_brain = bot_brain or BotBrain()

    @classmethod
    def from_loaded_state(cls, player_fleet: Fleet, bot_fleet: Fleet, loaded_state: GameState) -> "GameManager":
        manager = cls(player_fleet=player_fleet, bot_fleet=bot_fleet)
        manager.state = loaded_state

        manager.player_hits_on_bot = {
            cell for cell in bot_fleet.occupied_cells()
            if loaded_state.player_view.shots.get(cell) in (ShotOutcome.HIT, ShotOutcome.SUNK)
        }
        manager.bot_hits_on_player = {
            cell for cell in player_fleet.occupied_cells()
            if loaded_state.bot_view.shots.get(cell) in (ShotOutcome.HIT, ShotOutcome.SUNK)
        }

        return manager

    def is_game_over(self) -> GameResult:
        bot_cells = self.bot_fleet.occupied_cells()
        player_cells = self.player_fleet.occupied_cells()

        if bot_cells and self.player_hits_on_bot.issuperset(bot_cells):
            return GameResult(winner="player")
        if player_cells and self.bot_hits_on_player.issuperset(player_cells):
            return GameResult(winner="bot")
        return GameResult(winner=None)

    def apply_player_shot(self, target: Coordinate) -> ShotOutcome:
        if self.state.player_view.has_been_shot(target):
            raise ValueError("This cell was already shot/marked by the player.")
        return self._resolve_shot(
            target=target,
            defender_fleet=self.bot_fleet,
            shooter_hits=self.player_hits_on_bot,
            shooter_view=self.state.player_view,
        )

    def apply_bot_shot(self) -> tuple[Coordinate, ShotOutcome]:
        target = self.bot_brain.choose_next_shot(self.state.bot_view)
        if self.state.bot_view.has_been_shot(target):
            target = self._find_first_unshot_cell(self.state.bot_view)

        outcome = self._resolve_shot(
            target=target,
            defender_fleet=self.player_fleet,
            shooter_hits=self.bot_hits_on_player,
            shooter_view=self.state.bot_view,
        )
        self.bot_brain.on_shot_result(target, outcome)
        return target, outcome

    def commit_turn(self, player_target: Coordinate, player_outcome: ShotOutcome,
                    bot_target: Coordinate, bot_outcome: ShotOutcome) -> None:
        self.state.advance_turn()
        self.state.turn_history.append((
            Move(actor="player", target=player_target, outcome=player_outcome),
            Move(actor="bot", target=bot_target, outcome=bot_outcome),
        ))

    def _resolve_shot(self, target: Coordinate, defender_fleet: Fleet,
                      shooter_hits: Set[Coordinate], shooter_view: FogBoard) -> ShotOutcome:
        defender_cells = defender_fleet.occupied_cells()

        if target in defender_cells:
            shooter_hits.add(target)
            ship = defender_fleet.find_ship_containing(target)
            if ship is None:
                shooter_view.set_hit(target)
                return ShotOutcome.HIT

            ship_cells = ship.cell_set()
            if ship_cells.issubset(shooter_hits):
                for cell in ship_cells:
                    shooter_view.set_sunk(cell)
                self._mark_surrounding_as_miss(shooter_view, ship_cells)
                return ShotOutcome.SUNK

            shooter_view.set_hit(target)
            return ShotOutcome.HIT

        shooter_view.set_miss(target)
        return ShotOutcome.MISS

    @staticmethod
    def _mark_surrounding_as_miss(shooter_view: FogBoard, ship_cells: Set[Coordinate]) -> None:
        for ship_cell in ship_cells:
            for near in ship_cell.neighbors_8():
                if not near.is_inside():
                    continue
                if near in ship_cells:
                    continue
                shooter_view.set_miss(near)

    @staticmethod
    def _find_first_unshot_cell(board_view: FogBoard) -> Coordinate:
        for r in range(10):
            for c in range(10):
                cell = Coordinate(r, c)
                if not board_view.has_been_shot(cell):
                    return cell
        return Coordinate(0, 0)

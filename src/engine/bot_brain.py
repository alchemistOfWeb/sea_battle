import random
from dataclasses import dataclass
from typing import List, Optional

from src.domain import Coordinate, FogBoard, ShotOutcome


@dataclass
class TargetingState:
    hit_cells: List[Coordinate]
    axis: Optional[str] = None  # None, "h", "v"


class BotBrain:
    """
    Bot behavior:
    1) Random untested shots.
    2) After first hit: try adjacent (4-dir) cells.
    3) After second hit: lock axis and extend in both directions.
    Reset after SUNK.
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.targeting: Optional[TargetingState] = None

    def choose_next_shot(self, bot_view: FogBoard) -> Coordinate:
        if self.targeting is None:
            return self._random_unshot(bot_view)

        target = self._targeted_unshot(bot_view, self.targeting)
        if target is not None:
            return target

        return self._random_unshot(bot_view)

    def on_shot_result(self, target: Coordinate, outcome: ShotOutcome) -> None:
        if outcome == ShotOutcome.MISS:
            return
        if outcome == ShotOutcome.SUNK:
            self.targeting = None
            return

        if self.targeting is None:
            self.targeting = TargetingState(hit_cells=[target], axis=None)
            return

        self.targeting.hit_cells.append(target)

        if self.targeting.axis is None and len(self.targeting.hit_cells) >= 2:
            a, b = self.targeting.hit_cells[-2], self.targeting.hit_cells[-1]
            if a.row == b.row:
                self.targeting.axis = "h"
            elif a.col == b.col:
                self.targeting.axis = "v"

    def _random_unshot(self, bot_view: FogBoard) -> Coordinate:
        candidates: List[Coordinate] = []
        for r in range(10):
            for c in range(10):
                cell = Coordinate(r, c)
                if not bot_view.has_been_shot(cell):
                    candidates.append(cell)
        return self.rng.choice(candidates) if candidates else Coordinate(0, 0)

    def _targeted_unshot(self, bot_view: FogBoard, state: TargetingState) -> Optional[Coordinate]:
        if state.axis is None:
            last = state.hit_cells[-1]
            options = [c for c in last.neighbors_4() if c.is_inside() and not bot_view.has_been_shot(c)]
            return self.rng.choice(options) if options else None

        hits = state.hit_cells
        if state.axis == "h":
            row = hits[0].row
            cols = [c.col for c in hits if c.row == row]
            left_col, right_col = min(cols), max(cols)
            left = Coordinate(row, left_col - 1)
            right = Coordinate(row, right_col + 1)
            candidates = []
            if left.is_inside() and not bot_view.has_been_shot(left):
                candidates.append(left)
            if right.is_inside() and not bot_view.has_been_shot(right):
                candidates.append(right)
            return self.rng.choice(candidates) if candidates else None

        if state.axis == "v":
            col = hits[0].col
            rows = [c.row for c in hits if c.col == col]
            top_row, bottom_row = min(rows), max(rows)
            up = Coordinate(top_row - 1, col)
            down = Coordinate(bottom_row + 1, col)
            candidates = []
            if up.is_inside() and not bot_view.has_been_shot(up):
                candidates.append(up)
            if down.is_inside() and not bot_view.has_been_shot(down):
                candidates.append(down)
            return self.rng.choice(candidates) if candidates else None

        return None

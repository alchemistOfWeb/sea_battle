import random
from typing import List, Set

from src.domain import Coordinate, Fleet, Ship, BOARD_SIZE
from src.validators.fleet_validator import REQUIRED_SIZES


class RandomFleetGenerator:
    """
    Generates a random valid fleet (no overlap, no adjacency including diagonals).
    """

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def generate(self) -> Fleet:
        ships: List[Ship] = []
        occupied: Set[Coordinate] = set()
        forbidden: Set[Coordinate] = set()

        for size in REQUIRED_SIZES:
            ship = self._place_ship(size, occupied, forbidden)
            ships.append(ship)

            for cell in ship.cells:
                occupied.add(cell)
            for cell in ship.cells:
                for near in cell.neighbors_8():
                    if near.is_inside(BOARD_SIZE) and near not in occupied:
                        forbidden.add(near)

        return Fleet(ships=ships)

    def _place_ship(self, size: int, occupied: Set[Coordinate], forbidden: Set[Coordinate]) -> Ship:
        for _ in range(20_000):
            horizontal = self.rng.choice([True, False])
            if horizontal:
                row = self.rng.randrange(0, BOARD_SIZE)
                col_start = self.rng.randrange(0, BOARD_SIZE - size + 1)
                cells = [Coordinate(row, col_start + i) for i in range(size)]
            else:
                col = self.rng.randrange(0, BOARD_SIZE)
                row_start = self.rng.randrange(0, BOARD_SIZE - size + 1)
                cells = [Coordinate(row_start + i, col) for i in range(size)]

            if any(c in occupied for c in cells):
                continue
            if any(c in forbidden for c in cells):
                continue

            # Double-check adjacency to occupied cells
            ok = True
            for c in cells:
                for near in c.neighbors_8():
                    if near in occupied:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue

            return Ship(cells=cells)

        raise RuntimeError("Failed to generate a valid ship placement")

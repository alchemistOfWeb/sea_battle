from typing import List, Set

from src.domain import Coordinate, Fleet, Ship, BOARD_SIZE

REQUIRED_SIZES = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]


def validate_fleet_or_raise(fleet: Fleet) -> None:
    """Validates: sizes, inside board, straight/contiguous, no overlap, no adjacency (8-dir)."""
    ships = fleet.ships

    sizes = sorted([s.length for s in ships], reverse=True)
    if sorted(sizes) != sorted(REQUIRED_SIZES):
        raise ValueError(f"Invalid ship sizes: {sizes}. Required: {REQUIRED_SIZES}")

    occupied_cells: Set[Coordinate] = set()
    forbidden_cells: Set[Coordinate] = set()

    for ship in ships:
        _validate_ship_shape_or_raise(ship)

        for cell in ship.cells:
            if not cell.is_inside(BOARD_SIZE):
                raise ValueError(f"Ship cell out of bounds: {cell}")
            if cell in occupied_cells:
                raise ValueError(f"Overlapping ships at: {cell}")
            if cell in forbidden_cells:
                raise ValueError(f"Ships are touching (including diagonals) near: {cell}")

        for cell in ship.cells:
            occupied_cells.add(cell)

        for cell in ship.cells:
            for near in cell.neighbors_8():
                if near.is_inside(BOARD_SIZE) and near not in occupied_cells:
                    forbidden_cells.add(near)


def _validate_ship_shape_or_raise(ship: Ship) -> None:
    cells = ship.cells
    if not cells:
        raise ValueError("Empty ship")

    if len(cells) == 1:
        return

    rows = [c.row for c in cells]
    cols = [c.col for c in cells]

    is_horizontal = len(set(rows)) == 1
    is_vertical = len(set(cols)) == 1

    if not (is_horizontal or is_vertical):
        raise ValueError(f"Ship must be straight line: {cells}")

    if is_horizontal:
        sorted_cols = sorted(cols)
        start = min(sorted_cols)
        expected = list(range(start, start + len(sorted_cols)))
        if sorted_cols != expected:
            raise ValueError(f"Ship cells must be contiguous: {cells}")
        ship.cells = [c for c in sorted(cells, key=lambda x: x.col)]
        return

    sorted_rows = sorted(rows)
    start = min(sorted_rows)
    expected = list(range(start, start + len(sorted_rows)))
    if sorted_rows != expected:
        raise ValueError(f"Ship cells must be contiguous: {cells}")
    ship.cells = [c0 for c0 in sorted(cells, key=lambda x: x.row)]

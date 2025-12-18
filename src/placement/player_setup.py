from typing import List

from src.domain import Coordinate, Fleet, Ship
from src.validators.fleet_validator import REQUIRED_SIZES


class ConsoleFleetInput:
    """
    Reads 10 ships from console input. One ship per line.

    Supported formats:
    - "A1 A4" (two endpoints)
    - "A1" (single cell ship)
    - "1 1 1 4" (row1 col1 row2 col2), 1-based
    - "1,1 1,4" (two coords), 1-based or 0-based accepted
    """

    def read_fleet_from_console(self) -> Fleet:
        ships: List[Ship] = []
        for idx, size in enumerate(REQUIRED_SIZES, start=1):
            prompt = f"Ship {idx}/10 (size {size}) > "
            line = input(prompt).strip()
            cells = self._parse_ship_line(line)
            ships.append(Ship(cells=cells))
        return Fleet(ships=ships)

    def _parse_ship_line(self, line: str) -> List[Coordinate]:
        if not line:
            raise ValueError("Empty ship line")

        tokens = line.replace(";", " ").replace("|", " ").split()
        if len(tokens) == 1:
            return [self._parse_coordinate(tokens[0])]

        if len(tokens) == 2:
            a = self._parse_coordinate(tokens[0])
            b = self._parse_coordinate(tokens[1])
            return self._cells_from_endpoints(a, b)

        if len(tokens) == 4 and all(t.replace(",", "").isdigit() for t in tokens):
            r1, c1, r2, c2 = map(int, tokens)
            a = self._normalize_numeric(r1, c1)
            b = self._normalize_numeric(r2, c2)
            return self._cells_from_endpoints(a, b)

        raise ValueError("Unsupported ship input format")

    def _parse_coordinate(self, token: str) -> Coordinate:
        t = token.strip().upper()

        if t and t[0].isalpha():
            col_letter = t[0]
            if col_letter < "A" or col_letter > "J":
                raise ValueError("Column must be A..J")
            col = ord(col_letter) - ord("A")
            num_part = t[1:].strip()
            if not num_part.isdigit():
                raise ValueError("Row number expected after letter")
            row_1_based = int(num_part)
            if not (1 <= row_1_based <= 10):
                raise ValueError("Row must be 1..10")
            return Coordinate(row_1_based - 1, col)

        if "," in t:
            parts = [p for p in t.split(",") if p]
            if len(parts) != 2:
                raise ValueError("Bad r,c coordinate")
            r = int(parts[0])
            c = int(parts[1])
            return self._normalize_numeric(r, c)

        raise ValueError("Bad coordinate token")

    @staticmethod
    def _normalize_numeric(r: int, c: int) -> Coordinate:
        if 1 <= r <= 10 and 1 <= c <= 10:
            return Coordinate(r - 1, c - 1)
        if 0 <= r <= 9 and 0 <= c <= 9:
            return Coordinate(r, c)
        raise ValueError("Row/col must be 1..10 or 0..9")

    @staticmethod
    def _cells_from_endpoints(a: Coordinate, b: Coordinate) -> List[Coordinate]:
        if a == b:
            return [a]

        if a.row == b.row:
            r = a.row
            c1, c2 = sorted([a.col, b.col])
            return [Coordinate(r, c) for c in range(c1, c2 + 1)]

        if a.col == b.col:
            c = a.col
            r1, r2 = sorted([a.row, b.row])
            return [Coordinate(r, c) for r in range(r1, r2 + 1)]

        raise ValueError("Endpoints must form a straight ship (same row or same col)")

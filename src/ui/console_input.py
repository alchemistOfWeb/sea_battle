from src.domain import Coordinate
from src.ui.base import InputProvider


class ConsoleInputProvider(InputProvider):
    """
    Accepts:
      - A1..J10
      - "row col" or "row,col" (1-10 or 0-9 supported)
    """

    def read_shot_coordinate(self) -> Coordinate:
        while True:
            raw = input("Enter shot (e.g. A1, J10, '3 4', '2,7'): ").strip()
            try:
                return self._parse_coordinate(raw)
            except ValueError as e:
                print(f"Invalid input: {e}")

    def _parse_coordinate(self, s: str) -> Coordinate:
        s = s.strip().upper()
        if not s:
            raise ValueError("Empty input")

        if s[0].isalpha():
            col_letter = s[0]
            if col_letter < "A" or col_letter > "J":
                raise ValueError("Column must be A..J")
            col = ord(col_letter) - ord("A")
            num_part = s[1:].strip()
            if not num_part.isdigit():
                raise ValueError("Row number expected after letter (A1..J10)")
            row_1_based = int(num_part)
            if not (1 <= row_1_based <= 10):
                raise ValueError("Row must be 1..10")
            return Coordinate(row_1_based - 1, col)

        parts = s.replace(",", " ").split()
        if len(parts) != 2:
            raise ValueError("Expected two numbers: row and col")
        r = int(parts[0])
        c = int(parts[1])

        if 1 <= r <= 10 and 1 <= c <= 10:
            return Coordinate(r - 1, c - 1)
        if 0 <= r <= 9 and 0 <= c <= 9:
            return Coordinate(r, c)
        raise ValueError("Row/col must be 1..10 or 0..9")

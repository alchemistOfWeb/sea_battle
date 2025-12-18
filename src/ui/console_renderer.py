from src.domain import Coordinate, Fleet, GameState, ShotOutcome


class ConsoleRenderer:
    """
    Renders two 10x10 boards:
    - Left: player's own board (ships visible + bot shots).
    - Right: player's fog-of-war view of the enemy board.
    """

    def render(self, state: GameState, player_fleet: Fleet) -> None:
        own_lines = self._player_board_lines(state, player_fleet)
        enemy_lines = self._enemy_board_lines(state)

        gap = "   "
        print("\n" + "=" * 80)
        print(f"Turn: {state.turn_number}")
        print(f"{'YOUR BOARD':<36}{gap}{'ENEMY BOARD (FOG)':<36}")
        print("=" * 80)

        for left, right in zip(own_lines, enemy_lines):
            print(f"{left}{gap}{right}")

        print("\nLegend:")
        print("  Your board: S=ship, X=hit ship, o=miss, .=unknown water")
        print("  Enemy fog:  x=hit, o=miss, ?=unknown")
        print("=" * 80 + "\n")

    def _player_board_lines(self, state: GameState, player_fleet: Fleet) -> list[str]:
        occupied = player_fleet.occupied_cells()
        lines: list[str] = []
        lines.append("   " + " ".join(list("ABCDEFGHIJ")))

        for r in range(10):
            row_symbols: list[str] = []
            for c in range(10):
                cell = Coordinate(r, c)
                bot_mark = state.bot_view.shots.get(cell)

                if cell in occupied:
                    row_symbols.append("X" if bot_mark in (ShotOutcome.HIT, ShotOutcome.SUNK) else "S")
                else:
                    row_symbols.append("o" if bot_mark == ShotOutcome.MISS else ".")
            lines.append(f"{r+1:>2} " + " ".join(row_symbols))

        return lines

    def _enemy_board_lines(self, state: GameState) -> list[str]:
        lines: list[str] = []
        lines.append("   " + " ".join(list("ABCDEFGHIJ")))

        for r in range(10):
            row_symbols: list[str] = []
            for c in range(10):
                row_symbols.append(state.player_view.symbol_at(Coordinate(r, c)))
            lines.append(f"{r+1:>2} " + " ".join(row_symbols))

        return lines

# src/presentation/console_renderer.py
from typing import Optional, TYPE_CHECKING

from src.domain import BOARD_SIZE, Coordinate, FogCell

if TYPE_CHECKING:
    from src.domain import GameState, Fleet


class ConsoleGameRenderer:
    """
    Console renderer for the game.
    Shows two boards side-by-side:
    - Left: player's view of bot field (fog-of-war).
    - Right: bot's view of player field (fog-of-war).
    Optionally can show player's own ships on the right board.
    """

    def __init__(self, show_coordinates: bool = True):
        self.show_coordinates = show_coordinates

    def render(
        self,
        state: "GameState",
        player_fleet: Optional["Fleet"] = None,
        bot_fleet: Optional["Fleet"] = None,
        reveal_bot_ships: bool = False,
    ) -> None:
        title = f"Turn: {state.turn_number}"
        print("\n" + "=" * len(title))
        print(title)
        print("=" * len(title))

        left_title = "Your shots (enemy fog)"
        right_title = "Enemy shots (your fog)"

        left_lines = self._render_fog_board(
            state.player_view,
            title=left_title,
            overlay_fleet=(bot_fleet if reveal_bot_ships else None),
        )

        right_lines = self._render_fog_board(
            state.bot_view,
            title=right_title,
            overlay_fleet=player_fleet,  # show your ships under enemy shots
        )

        # Print side-by-side
        gap = "    "
        for l, r in zip(left_lines, right_lines):
            print(l + gap + r)

        print("")  # trailing blank line

    def _render_fog_board(self, fog_board, title: str, overlay_fleet: Optional["Fleet"]) -> list[str]:
        # Header: A..J
        cols = [chr(ord("A") + i) for i in range(BOARD_SIZE)]
        header = "    " + " ".join(cols) if self.show_coordinates else ""

        lines: list[str] = []
        lines.append(title)
        if self.show_coordinates:
            lines.append(header)

        fleet_cells = set()
        if overlay_fleet is not None:
            fleet_cells = overlay_fleet.occupied_cells()

        for row in range(BOARD_SIZE):
            row_cells = []
            for col in range(BOARD_SIZE):
                cell = Coordinate(row, col)
                symbol = fog_board.visible_symbol(cell)  # '?', 'o', 'x'

                # Overlay ships only for unknown cells (so hits/misses remain visible)
                if symbol == FogCell.UNKNOWN.value and cell in fleet_cells:
                    symbol = "■"  # ship cell

                row_cells.append(symbol)

            if self.show_coordinates:
                lines.append(f"{row + 1:>2}  " + " ".join(row_cells))
            else:
                lines.append(" ".join(row_cells))

        return lines

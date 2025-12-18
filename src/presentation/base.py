# src/presentation/interfaces.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.domain import GameState, Fleet


class GameRenderer(ABC):
    """Presentation layer interface. Gameplay must not depend on the output format."""

    @abstractmethod
    def render(
        self,
        state: "GameState",
        player_fleet: Optional["Fleet"] = None,
        bot_fleet: Optional["Fleet"] = None,
        reveal_bot_ships: bool = False,
    ) -> None:
        """
        Render current game state.
        - player_fleet is optional: allows showing player's own ships.
        - bot_fleet is optional: allows reveal mode (debug).
        """
        raise NotImplementedError

from abc import ABC, abstractmethod
from src.domain import Fleet, GameState


class FleetRepository(ABC):
    """Fleet storage interface (ships layout)."""

    @abstractmethod
    def save(self, fleet: Fleet) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self) -> Fleet:
        raise NotImplementedError


class GameStateRepository(ABC):
    """Game state storage interface (turns + boards)."""

    @abstractmethod
    def init_new(self, state: GameState) -> None:
        """Create a new game_state storage (e.g., write CSV header)."""
        raise NotImplementedError

    @abstractmethod
    def append_turn(self, state: GameState) -> None:
        """Append one record for the current turn."""
        raise NotImplementedError
    
    @abstractmethod
    def load(self) -> GameState:
        raise NotImplementedError

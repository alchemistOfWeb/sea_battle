from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain import Coordinate, Fleet, GameState


class Renderer(ABC):
    """Output layer. Can be replaced with GUI/web/etc."""

    @abstractmethod
    def render(self, state: "GameState", player_fleet: "Fleet") -> None:
        raise NotImplementedError


class InputProvider(ABC):
    """Input layer. Can be replaced with GUI/web/etc."""

    @abstractmethod
    def read_shot_coordinate(self) -> "Coordinate":
        raise NotImplementedError

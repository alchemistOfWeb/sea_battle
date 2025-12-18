from typing import Optional

from src.engine.game_manager import GameManager
from src.storage.base import GameStateRepository
from src.ui.console_renderer import ConsoleRenderer
from src.ui.console_input import ConsoleInputProvider


def run_cli_game(manager: GameManager, state_repo: Optional[GameStateRepository], resume: bool) -> None:
    """
    Controller loop for CLI.
    - Input: ConsoleInputProvider
    - Output: ConsoleRenderer
    - Persistence: GameStateRepository
    """
    renderer = ConsoleRenderer()
    input_provider = ConsoleInputProvider()

    # Show current state (including loaded state if resume=True)
    renderer.render(manager.state, manager.player_fleet)

    while True:
        result = manager.is_game_over()
        if result.winner is not None:
            print(f"Game over! Winner: {result.winner}")
            break

        # Player move (repeat if player shoots the same cell twice)
        while True:
            player_target = input_provider.read_shot_coordinate()
            try:
                player_outcome = manager.apply_player_shot(player_target)
                break
            except ValueError as e:
                print(e)

        # Bot move
        bot_target, bot_outcome = manager.apply_bot_shot()

        # Commit + persist
        manager.commit_turn(
            player_target=player_target, player_outcome=player_outcome,
            bot_target=bot_target, bot_outcome=bot_outcome,
        )
        if state_repo is not None:
            state_repo.append_turn(manager.state)

        renderer.render(manager.state, manager.player_fleet)

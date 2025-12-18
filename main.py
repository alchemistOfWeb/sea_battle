from pathlib import Path

from src.storage.csv_storage import CsvFleetRepository, CsvGameStateRepository
from src.placement.player_setup import ConsoleFleetInput
from src.placement.bot_setup import RandomFleetGenerator
from src.validators.fleet_validator import validate_fleet_or_raise
from src.engine.game_manager import GameManager
from src.gameplay import run_cli_game


DATA_DIR = Path("data")
PLAYER_SHIPS = DATA_DIR / "player_ships.csv"
BOT_SHIPS = DATA_DIR / "bot_ships.csv"
GAME_STATE = DATA_DIR / "game_state.csv"


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Path("outputs").mkdir(parents=True, exist_ok=True)

def main():
    ensure_dirs()

    player_repo = CsvFleetRepository(PLAYER_SHIPS)
    bot_repo = CsvFleetRepository(BOT_SHIPS)
    state_repo = CsvGameStateRepository(GAME_STATE)

    resume_available = GAME_STATE.exists() and PLAYER_SHIPS.exists() and BOT_SHIPS.exists()

    if resume_available:
        answer = input("Resume saved game? (y/n): ").strip().lower()
    else:
        answer = "n"

    if answer == "y":
        player_fleet = player_repo.load()
        bot_fleet = bot_repo.load()
        state = state_repo.load()

        validate_fleet_or_raise(player_fleet)
        validate_fleet_or_raise(bot_fleet)

        manager = GameManager.from_loaded_state(
            player_fleet=player_fleet,
            bot_fleet=bot_fleet,
            loaded_state=state,
        )
        print("Loaded saved game.")
        run_cli_game(manager, state_repo=state_repo, resume=True)
        return

    # New game
    print("\n=== Player ship placement ===")
    print("You will place ships on a 10x10 board. Ships must NOT touch, even diagonally.")
    print("Required ship sizes: 4, 3, 3, 2, 2, 2, 1, 1, 1, 1")
    print("Input format: one ship per line, e.g.: A1 A4  (or: 1 1 1 4)  (or: A1)\n")

    player_fleet = ConsoleFleetInput().read_fleet_from_console()
    validate_fleet_or_raise(player_fleet)
    player_repo.save(player_fleet)

    bot_fleet = RandomFleetGenerator().generate()
    validate_fleet_or_raise(bot_fleet)
    bot_repo.save(bot_fleet)

    manager = GameManager(player_fleet=player_fleet, bot_fleet=bot_fleet)
    state_repo.init_new(manager.state)

    run_cli_game(manager, state_repo=state_repo, resume=False)

if __name__ == "__main__":
    main()

# main.py
from pathlib import Path

from src.storage.csv_storage import CsvFleetRepository, CsvGameStateRepository
# from src.placement.player_setup import ConsoleFleetInput
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

    # NEW GAME (player fleet must be loaded from CSV)
    if not PLAYER_SHIPS.exists():
        print(f"Missing {PLAYER_SHIPS}. Create it first, then run again.")
        print("Format: ship_id,row,col (see README).")
        return

    player_fleet = player_repo.load()
    validate_fleet_or_raise(player_fleet)
    # bot_repo.save(bot_fleet)
    
    bot_fleet = RandomFleetGenerator().generate()
    validate_fleet_or_raise(bot_fleet)
    bot_repo.save(bot_fleet)

    manager = GameManager(player_fleet=player_fleet, bot_fleet=bot_fleet)

    # Start a fresh game_state.csv for a new game
    state_repo.init_new(manager.state)
    run_cli_game(manager, state_repo=state_repo, resume=False)

if __name__ == "__main__":
    main()

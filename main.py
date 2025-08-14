import importlib
from pathlib import Path
from datetime import datetime

GAMES = {
    "1": "azur_lane",
    "2": "blue_archive",
    "3": "brown_dust_2",
    "4": "lost_sword",
    "5": "nikke",
    "6": "resonance_solstice",
    "7": "silver_and_blood",
    "8": "starseed_asnia_trigger",
    "9": "trickcal_chibi_go"
}

def main():
    print("====================================")
    print("==== Vanilla's Sprite Extractor ====")
    print("====================================\n")
    print("Select a game to extract from:")
    for k, v in GAMES.items():
        print(f"{k}. {v.replace('_', ' ').title()}")
    print("0. Exit")

    choice = input("\nEnter choice: ").strip()
    if choice == "0":
        print("Exiting program. Goodbye!")
        return
    if choice not in GAMES:
        print("[ERROR] Invalid choice.")
        return

    game_name = GAMES[choice]

    timestamp = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
    output_folder = Path("output") / f"{game_name}_{timestamp}"
    output_folder.mkdir(parents=True, exist_ok=True)

    game_module = importlib.import_module(f"games.{game_name}")

    if hasattr(game_module, "run"):
        game_module.run(output_folder)
    else:
        print(f"[ERROR] Game module '{game_name}' has no run(output_folder) function.")

if __name__ == "__main__":
    main()

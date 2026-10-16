from pathlib import Path

DATASET_DIR = Path(
    r"C:\Users\DELL\Downloads\Pokemon-Dataset-Extracted\PokemonData"
)

if not DATASET_DIR.exists():
    print("ERROR: Dataset folder not found.")
else:
    pokemon_folders = [
        folder for folder in DATASET_DIR.iterdir()
        if folder.is_dir()
    ]

    print("Dataset path:", DATASET_DIR)
    print("Number of Pokemon classes:", len(pokemon_folders))

    pikachu_folder = DATASET_DIR / "Pikachu"

    if pikachu_folder.exists():
        image_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        images = [
            file for file in pikachu_folder.iterdir()
            if file.is_file()
            and file.suffix.lower() in image_extensions
        ]

        print("Pikachu images:", len(images))
    else:
        print("Pikachu folder not found.")

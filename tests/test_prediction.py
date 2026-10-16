
from pathlib import Path

from PIL import Image

from backend.services.prediction_service import predict_pokemon


DATASET_DIR = Path(
    r"C:\Users\DELL\Downloads\Pokemon-Dataset-Extracted\PokemonData"
)


def main():
    image_path = DATASET_DIR / "Pikachu"

    if not image_path.is_dir():
        raise FileNotFoundError(
            f"Pikachu dataset folder not found: {image_path}"
        )

    image_files = [
        path for path in image_path.iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    ]

    if not image_files:
        raise FileNotFoundError("No Pikachu images found.")

    with Image.open(image_files[0]) as image:
        result = predict_pokemon(image.copy())

    print("Test image:", image_files[0].name)
    print("Predicted Pokémon:", result["pokemon"])
    print("Confidence:", f'{result["confidence"]}%')


if __name__ == "__main__":
    main()

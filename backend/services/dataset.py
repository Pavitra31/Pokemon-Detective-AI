
import csv
from pathlib import Path

from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / "datasets" / "pokemon_clean_manifest.csv"

IMAGE_SIZE = 224
BATCH_SIZE = 4
RANDOM_STATE = 42

NORMALIZE = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225],
)

TRAIN_TRANSFORM = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=10),
    transforms.ColorJitter(
        brightness=0.15,
        contrast=0.15,
        saturation=0.15,
        hue=0.03,
    ),
    transforms.ToTensor(),
    NORMALIZE,
])

VALIDATION_TRANSFORM = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    NORMALIZE,
])


class ManifestDataset(Dataset):
    def __init__(self, rows, classes, transform=None):
        self.rows = rows
        self.classes = classes
        self.class_to_idx = {
            name: index for index, name in enumerate(classes)
        }
        self.transform = transform

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        image_path = Path(row["destination_file"])

        with Image.open(image_path) as image:
            image = image.convert("RGB")

        if self.transform:
            image = self.transform(image)

        label = self.class_to_idx[row["pokemon"]]
        return image, label


def load_datasets():
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(
            f"Clean manifest not found: {MANIFEST_PATH}"
        )

    with MANIFEST_PATH.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise RuntimeError("Clean manifest is empty.")

    classes = sorted({row["pokemon"] for row in rows})
    class_to_idx = {
        name: index for index, name in enumerate(classes)
    }

    counts = {name: 0 for name in classes}
    for row in rows:
        counts[row["pokemon"]] += 1

        image_path = Path(row["destination_file"])
        if not image_path.is_file():
            raise FileNotFoundError(
                f"Manifest image missing: {image_path}"
            )

    too_small = [
        name for name, count in counts.items() if count < 2
    ]
    if too_small:
        raise RuntimeError(
            "Classes need at least two images for a stratified split: "
            + ", ".join(too_small[:20])
        )

    indices = list(range(len(rows)))
    labels = [class_to_idx[row["pokemon"]] for row in rows]

    train_indices, validation_indices = train_test_split(
        indices,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    train_rows = [rows[i] for i in train_indices]
    validation_rows = [rows[i] for i in validation_indices]

    train_dataset = ManifestDataset(
        train_rows, classes, TRAIN_TRANSFORM
    )
    validation_dataset = ManifestDataset(
        validation_rows, classes, VALIDATION_TRANSFORM
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )
    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    print("Clean manifest:", MANIFEST_PATH)
    print("Pokémon classes:", len(classes))
    print("Clean images:", len(rows))
    print("Training images:", len(train_dataset))
    print("Validation images:", len(validation_dataset))

    return train_loader, validation_loader, classes

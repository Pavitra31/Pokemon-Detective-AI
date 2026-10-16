
import torch

from backend.services.dataset import MANIFEST_PATH, load_datasets


def main():
    train_loader, validation_loader, classes = load_datasets()

    print("Clean manifest:", MANIFEST_PATH)
    print("Number of Pokemon classes:", len(classes))

    images, labels = next(iter(train_loader))

    print("Image batch shape:", images.shape)
    print("Label batch shape:", labels.shape)
    print("First labels:", labels.tolist())
    print("Training images:", len(train_loader.dataset))
    print("Validation images:", len(validation_loader.dataset))

    assert len(classes) == 1012
    assert images.shape[1:] == (3, 224, 224)
    assert labels.dtype == torch.int64
    assert labels.min().item() >= 0
    assert labels.max().item() < len(classes)
    assert len(train_loader.dataset) + len(validation_loader.dataset) == 59534

    print("Clean dataset loader test passed!")


if __name__ == "__main__":
    main()

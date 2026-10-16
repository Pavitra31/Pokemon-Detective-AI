
from pathlib import Path

import torch
from torch import nn
from torchvision import models

from backend.services.dataset import load_datasets

CHECKPOINT_PATH = Path("models/pokemon_efficientnet_b0_1012_fulltrained.pth")
DEVICE = torch.device("cpu")


def main():
    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(f"Checkpoint not found: {CHECKPOINT_PATH}")

    print("Loading checkpoint...")
    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=DEVICE,
        weights_only=False,
    )

    checkpoint_classes = checkpoint["classes"]

    print("Loading clean dataset...")
    _, validation_loader, dataset_classes = load_datasets()

    if list(dataset_classes) != list(checkpoint_classes):
        raise ValueError(
            "Dataset class order does not match the checkpoint. "
            "Evaluation stopped to avoid misleading results."
        )

    model = models.efficientnet_b0(weights=None)
    model.classifier[1] = nn.Linear(
        model.classifier[1].in_features,
        len(checkpoint_classes),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(DEVICE)
    model.eval()

    correct_top1 = 0
    correct_top5 = 0
    total = 0
    total_batches = len(validation_loader)

    print(f"Evaluating {len(validation_loader.dataset)} validation images...")

    with torch.inference_mode():
        for batch_index, (images, labels) in enumerate(
            validation_loader, start=1
        ):
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            logits = model(images)
            top5_indices = logits.topk(
                min(5, len(checkpoint_classes)), dim=1
            ).indices

            correct_top1 += (
                top5_indices[:, 0] == labels
            ).sum().item()

            correct_top5 += (
                top5_indices == labels.unsqueeze(1)
            ).any(dim=1).sum().item()

            total += labels.size(0)

            if batch_index % 500 == 0 or batch_index == total_batches:
                print(
                    f"Progress: {total}/{len(validation_loader.dataset)} images"
                )

    top1 = 100 * correct_top1 / total
    top5 = 100 * correct_top5 / total

    print("\nFULL VALIDATION RESULTS")
    print(f"Images evaluated: {total}")
    print(f"Top-1 accuracy: {top1:.2f}%")
    print(f"Top-5 accuracy: {top5:.2f}%")
    print(
        "Checkpoint recorded accuracy: "
        f"{checkpoint['validation_accuracy']:.2f}%"
    )
    print(f"Classes verified: {len(checkpoint_classes)}")
    print("Evaluation complete.")


if __name__ == "__main__":
    main()

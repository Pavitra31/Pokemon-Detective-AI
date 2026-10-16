
from pathlib import Path
import copy
import time

import torch
import torch.nn as nn
from torch.optim import AdamW

from backend.services.dataset import load_datasets
from backend.services.vision_model import create_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEVICE = torch.device("cpu")

SOURCE_CHECKPOINT = (
    PROJECT_ROOT / "models" / "pokemon_efficientnet_b0_1012_finetuned.pth"
)
OUTPUT_CHECKPOINT = (
    PROJECT_ROOT / "models" / "pokemon_efficientnet_b0_1012_fulltrained.pth"
)

EPOCHS = 5
BATCH_SIZE = 4
FEATURES_LR = 0.00001
CLASSIFIER_LR = 0.0001
PATIENCE = 2
RANDOM_SEED = 42


def evaluate(model, loader):
    model.eval()
    correct1 = 0
    correct5 = 0
    total = 0

    with torch.inference_mode():
        for images, labels in loader:
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)
            outputs = model(images)

            correct1 += outputs.argmax(1).eq(labels).sum().item()
            correct5 += (
                outputs.topk(5, dim=1).indices
                .eq(labels[:, None]).any(dim=1).sum().item()
            )
            total += labels.size(0)

    return 100 * correct1 / total, 100 * correct5 / total


def main():
    torch.manual_seed(RANDOM_SEED)
    torch.set_num_threads(4)

    if not SOURCE_CHECKPOINT.is_file():
        raise FileNotFoundError(f"Missing checkpoint: {SOURCE_CHECKPOINT}")

    if OUTPUT_CHECKPOINT.exists():
        raise FileExistsError(
            f"Output already exists; choose a new filename: {OUTPUT_CHECKPOINT}"
        )

    print("Loading complete clean dataset...")
    train_loader, val_loader, classes = load_datasets()

    checkpoint = torch.load(
        SOURCE_CHECKPOINT,
        map_location=DEVICE,
        weights_only=True,
    )

    if checkpoint["classes"] != classes:
        raise ValueError("Checkpoint and dataset class order do not match.")

    model = create_model(num_classes=len(classes), pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(DEVICE)

    # Fine-tune the final feature block and classification head.
    for parameter in model.features.parameters():
        parameter.requires_grad = False

    for parameter in model.features[-1].parameters():
        parameter.requires_grad = True

    for parameter in model.classifier.parameters():
        parameter.requires_grad = True

    optimizer = AdamW(
        [
            {
                "params": model.features[-1].parameters(),
                "lr": FEATURES_LR,
            },
            {
                "params": model.classifier.parameters(),
                "lr": CLASSIFIER_LR,
            },
        ],
        weight_decay=0.0001,
    )

    criterion = nn.CrossEntropyLoss()
    best_top1 = -1.0
    best_state = copy.deepcopy(model.state_dict())
    epochs_without_improvement = 0
    start = time.time()

    print(f"Training images: {len(train_loader.dataset)}")
    print(f"Validation images: {len(val_loader.dataset)}")
    print(f"Classes: {len(classes)}")
    print(f"Maximum epochs: {EPOCHS}")
    print("Training starts. This may take many hours on CPU.")

    for epoch in range(EPOCHS):
        model.train()

        # Keep frozen feature blocks in evaluation mode.
        for layer in model.features[:-1]:
            layer.eval()

        total_loss = 0.0
        total_samples = 0

        for batch_idx, (images, labels) in enumerate(train_loader, start=1):
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad(set_to_none=True)
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            batch_size = labels.size(0)
            total_loss += loss.item() * batch_size
            total_samples += batch_size

            if batch_idx % 500 == 0:
                print(
                    f"Epoch {epoch + 1}/{EPOCHS} | "
                    f"Batch {batch_idx}/{len(train_loader)} | "
                    f"Loss {loss.item():.4f}",
                    flush=True,
                )

        top1, top5 = evaluate(model, val_loader)
        average_loss = total_loss / max(total_samples, 1)

        print(
            f"\nEpoch {epoch + 1}/{EPOCHS} complete | "
            f"Loss: {average_loss:.4f} | "
            f"Validation top-1: {top1:.2f}% | "
            f"Validation top-5: {top5:.2f}%",
            flush=True,
        )

        if top1 > best_top1:
            best_top1 = top1
            best_state = copy.deepcopy(model.state_dict())
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= PATIENCE:
            print("Early stopping: validation accuracy did not improve.")
            break

    torch.save(
        {
            "model_state_dict": best_state,
            "classes": classes,
            "validation_accuracy": best_top1,
            "epochs_completed": epoch + 1,
            "training_images": len(train_loader.dataset),
            "validation_images": len(val_loader.dataset),
            "trial": False,
        },
        OUTPUT_CHECKPOINT,
    )

    print("\nFull-data fine-tuning finished.")
    print(f"Best validation top-1: {best_top1:.2f}%")
    print(f"Elapsed minutes: {(time.time() - start) / 60:.1f}")
    print(f"Saved new checkpoint: {OUTPUT_CHECKPOINT}")


if __name__ == "__main__":
    main()

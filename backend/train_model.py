
from pathlib import Path
import random
import time
from collections import defaultdict

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Subset

from backend.services.dataset import load_datasets
from backend.services.vision_model import create_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEVICE = torch.device("cpu")

# Controlled experiment settings
TRAIN_IMAGES_PER_CLASS = 10
MAX_VALIDATION_IMAGES = 1012
BATCH_SIZE = 4
EPOCHS = 2
RANDOM_SEED = 42

MODEL_OUTPUT = (
    PROJECT_ROOT
    / "models"
    / "pokemon_efficientnet_b0_1012_experiment.pth"
)


def select_balanced_indices(dataset, limit_per_class):
    """Select up to limit_per_class images for each class."""
    by_class = defaultdict(list)

    for index, row in enumerate(dataset.rows):
        by_class[row["pokemon"]].append(index)

    random.seed(RANDOM_SEED)
    selected = []

    for indices in by_class.values():
        random.shuffle(indices)
        selected.extend(indices[:limit_per_class])

    random.shuffle(selected)
    return selected


def main():
    torch.manual_seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)

    print("Training device:", DEVICE)
    print("Loading clean dataset...")

    full_train_loader, full_validation_loader, classes = load_datasets()

    train_dataset = full_train_loader.dataset
    validation_dataset = full_validation_loader.dataset

    train_indices = select_balanced_indices(
        train_dataset,
        TRAIN_IMAGES_PER_CLASS,
    )

    # Use a fixed validation sample to make experiments comparable.
    validation_indices = list(range(len(validation_dataset)))
    random.shuffle(validation_indices)
    validation_indices = validation_indices[:MAX_VALIDATION_IMAGES]

    experiment_train = Subset(train_dataset, train_indices)
    experiment_validation = Subset(
        validation_dataset,
        validation_indices,
    )

    train_loader = DataLoader(
        experiment_train,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )

    validation_loader = DataLoader(
        experiment_validation,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    print("Number of classes:", len(classes))
    print("Experiment training images:", len(experiment_train))
    print("Experiment validation images:", len(experiment_validation))
    print("Training batches per epoch:", len(train_loader))
    print("Epochs:", EPOCHS)

    print("Initializing pretrained EfficientNet-B0...")
    model = create_model(
        num_classes=len(classes),
        pretrained=True,
    )
    model.to(DEVICE)

    # Train the classifier first while keeping image features frozen.
    for parameter in model.features.parameters():
        parameter.requires_grad = False

    for parameter in model.classifier.parameters():
        parameter.requires_grad = True

    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(
        model.classifier.parameters(),
        lr=0.0005,
        weight_decay=0.0001,
    )

    MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    best_accuracy = -1.0

    for epoch in range(EPOCHS):
        model.train()
        model.features.eval()
        model.classifier.train()

        running_loss = 0.0
        processed = 0

        print(f"\nStarting epoch {epoch + 1}/{EPOCHS}...")

        for batch_index, (images, labels) in enumerate(
            train_loader,
            start=1,
        ):
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            processed += labels.size(0)

            if batch_index % 100 == 0:
                print(
                    f"Epoch {epoch + 1}/{EPOCHS} | "
                    f"Batch {batch_index}/{len(train_loader)} | "
                    f"Images processed: {processed} | "
                    f"Loss: {loss.item():.4f}"
                )

        average_loss = running_loss / len(train_loader)

        # Evaluate only on the fixed validation sample.
        model.eval()
        correct_top1 = 0
        correct_top5 = 0
        total = 0

        with torch.inference_mode():
            for images, labels in validation_loader:
                images = images.to(DEVICE)
                labels = labels.to(DEVICE)

                outputs = model(images)
                predictions = outputs.argmax(dim=1)
                top5 = outputs.topk(5, dim=1).indices

                correct_top1 += (predictions == labels).sum().item()
                correct_top5 += (
                    (top5 == labels.unsqueeze(1))
                    .any(dim=1)
                    .sum()
                    .item()
                )
                total += labels.size(0)

        top1_accuracy = 100.0 * correct_top1 / total
        top5_accuracy = 100.0 * correct_top5 / total

        print(f"Epoch {epoch + 1} average loss: {average_loss:.4f}")
        print(f"Validation top-1 accuracy: {top1_accuracy:.2f}%")
        print(f"Validation top-5 accuracy: {top5_accuracy:.2f}%")

        if top1_accuracy > best_accuracy:
            best_accuracy = top1_accuracy

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "classes": classes,
                    "epoch": epoch + 1,
                    "validation_accuracy": top1_accuracy,
                    "validation_top5_accuracy": top5_accuracy,
                    "training_images": len(experiment_train),
                    "trial": True,
                },
                MODEL_OUTPUT,
            )
            print("Best experiment checkpoint saved:", MODEL_OUTPUT)

    print("\n========== EXPERIMENT RESULTS ==========")
    print(f"Best validation top-1 accuracy: {best_accuracy:.2f}%")
    print(f"Elapsed time: {(time.time() - start_time) / 60:.1f} minutes")
    print("Checkpoint:", MODEL_OUTPUT)
    print("Original checkpoints were not overwritten.")
    print("========================================")


if __name__ == "__main__":
    main()

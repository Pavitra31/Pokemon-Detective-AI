
import torch

from backend.services.dataset import load_datasets
from backend.services.vision_model import create_model


def main():
    _, _, classes = load_datasets()

    model = create_model(num_classes=len(classes))
    model.eval()

    sample_images = torch.randn(2, 3, 224, 224)

    with torch.no_grad():
        predictions = model(sample_images)

    print("Number of classes:", len(classes))
    print("Model output shape:", predictions.shape)
    print("Model test passed!")


if __name__ == "__main__":
    main()

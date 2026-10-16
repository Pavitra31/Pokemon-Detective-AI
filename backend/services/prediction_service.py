
from functools import lru_cache
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

from backend.services.vision_model import create_model
from backend.services.color_service import extract_dominant_color


MODEL_PATH = Path("models/pokemon_efficientnet_b0_1012_fulltrained.pth")
DEVICE = torch.device("cpu")

IMAGE_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


@lru_cache(maxsize=1)
def load_trained_model():
    """Load the trained model once and reuse it for later predictions."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH.resolve()}"
        )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=True,
    )

    classes = checkpoint["classes"]
    model = create_model(num_classes=len(classes))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(DEVICE)
    model.eval()

    return model, classes


def predict_pokemon(image: Image.Image):
    image = image.convert("RGB")
    dominant_color = extract_dominant_color(image)

    image_tensor = IMAGE_TRANSFORM(image).unsqueeze(0)
    model, classes = load_trained_model()

    with torch.inference_mode():
        outputs = model(image_tensor.to(DEVICE))
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted_index = probabilities.max(dim=1)

    return {
        "pokemon": classes[predicted_index.item()],
        "confidence": round(confidence.item() * 100, 2),
        "dominant_color": dominant_color,
    }

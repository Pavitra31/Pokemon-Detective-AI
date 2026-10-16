
import torch.nn as nn
from torchvision import models


def create_model(num_classes=1012, pretrained=True):
    weights = (
        models.EfficientNet_B0_Weights.DEFAULT
        if pretrained
        else None
    )

    model = models.efficientnet_b0(weights=weights)
    input_features = model.classifier[1].in_features

    model.classifier[1] = nn.Linear(
        input_features,
        num_classes,
    )

    return model

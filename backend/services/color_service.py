
from collections import Counter, deque

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def remove_edge_background(pixels: np.ndarray, threshold: float = 35.0):
    """
    Identify background pixels connected to the image edges.

    This works best for images with a reasonably uniform background,
    such as Pokémon artwork on black or white backgrounds.
    """
    height, width, _ = pixels.shape
    background_mask = np.zeros((height, width), dtype=bool)
    visited = np.zeros((height, width), dtype=bool)

    # Use the four corners as background-color references.
    corners = [
        pixels[0, 0],
        pixels[0, width - 1],
        pixels[height - 1, 0],
        pixels[height - 1, width - 1],
    ]

    queue = deque()

    # Start from edge pixels that resemble a corner background color.
    for x in range(width):
        for y in (0, height - 1):
            if any(
                np.linalg.norm(
                    pixels[y, x].astype(float) - color.astype(float)
                ) <= threshold
                for color in corners
            ):
                queue.append((y, x))

    for y in range(height):
        for x in (0, width - 1):
            if any(
                np.linalg.norm(
                    pixels[y, x].astype(float) - color.astype(float)
                ) <= threshold
                for color in corners
            ):
                queue.append((y, x))

    while queue:
        y, x = queue.popleft()

        if visited[y, x]:
            continue

        visited[y, x] = True

        current = pixels[y, x].astype(float)

        # Only remove pixels connected to an edge and similar
        # to at least one detected corner background color.
        if not any(
            np.linalg.norm(current - color.astype(float)) <= threshold
            for color in corners
        ):
            continue

        background_mask[y, x] = True

        for ny, nx in (
            (y - 1, x),
            (y + 1, x),
            (y, x - 1),
            (y, x + 1),
        ):
            if (
                0 <= ny < height
                and 0 <= nx < width
                and not visited[ny, nx]
            ):
                queue.append((ny, nx))

    return background_mask


def extract_dominant_color(
    image: Image.Image,
    clusters: int = 3,
) -> str:
    """
    Extract a dominant Pokémon color while ignoring edge-connected
    background pixels. Returns a hexadecimal RGB color.
    """
    image = image.convert("RGBA")
    image.thumbnail((120, 120))

    rgba = np.asarray(image, dtype=np.uint8)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    # Ignore transparent pixels.
    visible_mask = alpha > 20

    # Remove background connected to the edges.
    background_mask = remove_edge_background(rgb)
    pokemon_mask = visible_mask & ~background_mask

    # If segmentation removed almost everything, fall back to
    # visible pixels rather than returning an unusable result.
    if np.count_nonzero(pokemon_mask) < 30:
        pokemon_mask = visible_mask

    pixels = rgb[pokemon_mask]

    if len(pixels) == 0:
        return "#f5c542"

    unique_pixels = np.unique(pixels, axis=0)
    cluster_count = min(clusters, len(unique_pixels))

    if cluster_count == 1:
        dominant_rgb = unique_pixels[0]
    else:
        model = KMeans(
            n_clusters=cluster_count,
            random_state=42,
            n_init=3,
        )
        labels = model.fit_predict(pixels.astype(np.float32))

        dominant_label = Counter(labels).most_common(1)[0][0]
        dominant_rgb = np.clip(
            model.cluster_centers_[dominant_label],
            0,
            255,
        ).astype(int)

    return "#{:02x}{:02x}{:02x}".format(*dominant_rgb)

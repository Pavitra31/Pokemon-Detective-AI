
from io import BytesIO
from unittest.mock import patch

import pytest
from PIL import Image

from backend.app import app


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,
    )
    with app.test_client() as test_client:
        yield test_client


def make_test_image():
    image_bytes = BytesIO()
    Image.new("RGB", (32, 32), color="red").save(
        image_bytes, format="PNG"
    )
    image_bytes.seek(0)
    return image_bytes


def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    data = response.get_json()
    assert data["project"] == "Pokémon Detective AI"


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_predict_without_image_returns_400(client):
    response = client.post("/api/predict")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_predict_with_empty_file_returns_400(client):
    response = client.post(
        "/api/predict",
        data={"image": (BytesIO(b""), "empty.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "The uploaded file is empty"


def test_predict_with_invalid_image_returns_400(client):
    response = client.post(
        "/api/predict",
        data={"image": (BytesIO(b"not an image"), "invalid.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert "Invalid image" in response.get_json()["error"]


def test_predict_with_valid_image_returns_prediction(client):
    expected = {
        "pokemon": "Pikachu",
        "confidence": 95.5,
        "dominant_color": "#ff0000",
    }

    with patch("backend.app.predict_pokemon", return_value=expected) as mocked:
        response = client.post(
            "/api/predict",
            data={"image": (make_test_image(), "pikachu.png")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    assert response.get_json() == expected
    mocked.assert_called_once()


def test_pokemon_details_success(client):
    expected = {
        "id": 25,
        "name": "Pikachu",
        "height_m": 0.4,
        "weight_kg": 6.0,
        "types": ["electric"],
        "abilities": ["static"],
        "stats": {"speed": 90},
        "image": "https://example.com/pikachu.png",
    }

    with patch(
        "backend.app.get_pokemon_details",
        return_value=expected,
    ) as mocked:
        response = client.get("/api/pokemon/pikachu")

    assert response.status_code == 200
    assert response.get_json() == expected
    mocked.assert_called_once_with("pikachu")


def test_unknown_pokemon_returns_404(client):
    with patch("backend.app.get_pokemon_details", return_value=None):
        response = client.get("/api/pokemon/notarealpokemon")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Pokémon not found"


def test_pokedex_network_error_returns_502(client):
    from requests.exceptions import ConnectionError

    with patch(
        "backend.app.get_pokemon_details",
        side_effect=ConnectionError("network unavailable"),
    ):
        response = client.get("/api/pokemon/pikachu")

    assert response.status_code == 502
    assert response.get_json()["error"] == "Unable to retrieve Pokémon data"


def test_oversized_image_returns_413(client):
    app.config["MAX_CONTENT_LENGTH"] = 10

    response = client.post(
        "/api/predict",
        data={"image": (BytesIO(b"x" * 100), "large.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert "too large" in response.get_json()["error"].lower()

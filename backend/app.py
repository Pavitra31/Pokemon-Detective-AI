import os
from io import BytesIO
from flask_cors import CORS
from flask import Flask, jsonify, request
from PIL import Image, UnidentifiedImageError
from requests.exceptions import RequestException

from backend.services.pokedex_service import get_pokemon_details
from backend.services.prediction_service import predict_pokemon


app = Flask(__name__)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

CORS(app, resources={r"/api/*": {"origins": allowed_origins}})


# Limit uploaded images to 10 MB.
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.route("/")
def home():
    return jsonify({
        "project": "Pokémon Detective AI",
        "message": "Welcome, Detective! The backend is running."
    })


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "project": "Pokémon Detective AI"
    })


@app.route("/api/pokemon/<name>")
def pokemon_details(name):
    try:
        pokemon = get_pokemon_details(name)

        if pokemon is None:
            return jsonify({
                "error": "Pokémon not found"
            }), 404

        return jsonify(pokemon), 200

    except RequestException:
        app.logger.exception("PokéAPI request failed")
        return jsonify({
            "error": "Unable to retrieve Pokémon data"
        }), 502


@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({
            "error": "Please upload an image using the 'image' field"
        }), 400

    uploaded_file = request.files["image"]

    if not uploaded_file.filename:
        return jsonify({
            "error": "No image selected"
        }), 400

    try:
        image_bytes = uploaded_file.read()

        if not image_bytes:
            return jsonify({
                "error": "The uploaded file is empty"
            }), 400

        with Image.open(BytesIO(image_bytes)) as image:
            image.load()
            result = predict_pokemon(image.copy())

        return jsonify(result), 200

    except UnidentifiedImageError:
        return jsonify({
            "error": "Invalid image file. Please upload a valid image."
        }), 400

    except Exception:
        app.logger.exception("Pokémon prediction failed")
        return jsonify({
            "error": "Unable to predict Pokémon"
        }), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "Image is too large. Maximum upload size is 10 MB."
    }), 413


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )

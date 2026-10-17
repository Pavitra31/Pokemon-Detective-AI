# Pokémon Detective AI 🔎⚡

**A Detective Pikachu-inspired Pokémon investigation experience powered by computer vision.**

Pokémon Detective AI lets you upload a Pokémon image, identify the most likely Pokémon using a trained **EfficientNet-B0** model, inspect its Pokédex profile, and explore a detective-themed interface with animated scanning and a color palette derived from the uploaded image.



## Highlights

- **AI Image Classification:** Predicts a Pokémon class and returns a confidence score.
- **Pokédex Investigation:** Retrieves types, abilities, dimensions, base stats, and artwork through PokéAPI.
- **Image-Derived Colors:** Extracts dominant colors from the uploaded image for the visual theme.
- **Detective-Inspired UI:** Animated scanning and reveal interactions.
- **React + Flask Architecture:** A Vite-powered React frontend communicates with a Python Flask REST API.
- **Validation and Error Handling:** Handles image requests and common API errors.

## How It Works

1. Upload an image of one Pokémon.
2. Preprocess the image for the model.
3. Run EfficientNet-B0 to predict a class and calculate confidence.
4. Retrieve Pokédex information through PokéAPI.
5. Extract dominant colors from the uploaded image.
6. Present the result with Pokémon details and the detective-themed interface.

```text
Image upload
    ↓
Flask API validates the image
    ↓
PyTorch / EfficientNet-B0 prediction
    ↓
PokéAPI lookup + dominant-color extraction
    ↓
Pokémon profile + confidence + themed UI
```

## Technology Stack

| Area                 | Technology                            |
| -------------------- | ------------------------------------- |
| Frontend             | React, Vite, JavaScript, CSS          |
| Backend              | Python, Flask, Flask-CORS             |
| Image Classification | PyTorch, Torchvision, EfficientNet-B0 |
| Image Handling       | Pillow                                |
| Pokémon Data         | PokéAPI, Requests                     |
| Testing              | pytest                                |
| Version Control      | Git, GitHub                           |

The repository's `package.json` and `requirements.txt` are the source of truth for installed dependencies.

## Model and Dataset

- **Architecture:** EfficientNet-B0
- **Input Size:** 224 × 224 pixels
- **Classes:** 1,012 Pokémon classes
- **Dataset Images:** 59,534
  - Training: 47,627
  - Validation: 11,907

### Recorded Validation Results

| Metric         | Result |
| -------------- | -----: |
| Top-1 Accuracy | 62.96% |
| Top-5 Accuracy | 78.37% |

These figures are from the recorded five-epoch validation run. They do not guarantee correct identification for every image. Results can vary with image quality, background, pose, class imbalance, and similarity between Pokémon.

**Model weights are not included in this repository.** The `.gitignore` excludes `.pth`, `.pt`, and `.onnx` files, so a compatible checkpoint must be obtained or generated separately before running prediction. Do not commit datasets, model checkpoints, credentials, or `.env` files.

## Project Structure

```text
Pokemon-Detective-AI/
├── backend/
│   ├── app.py
│   └── services/
│       ├── color_service.py
│       ├── dataset.py
│       ├── pokedex_service.py
│       ├── prediction_service.py
│       └── vision_model.py
├── frontend/
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── PikachuDetective.jsx
│       └── PikachuDetective.css
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Run Locally

### Requirements

- Python 3.12 or a compatible version for the installed dependencies
- Node.js and npm
- The trained model checkpoint expected by the backend (not included in Git)

### 1. Set Up the Backend

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Place a compatible checkpoint in the `models/` location expected by the model-loading code. The checkpoint is intentionally excluded from Git.

Start Flask from the repository root:

```powershell
python -m backend.app
```

The API is expected at `http://127.0.0.1:5000`.

### 2. Set Up the Frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

### 3. Test the API

The backend provides a prediction endpoint at `/api/predict` that accepts an image as multipart form data, and a Pokémon information endpoint at `/api/pokemon/<name>`. With the backend running:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/pokemon/pikachu
```

The prediction endpoint requires a compatible checkpoint. See `backend/app.py` for current route definitions and request format.

## Tests

Run the Python tests from the repository root:

```powershell
python -m pytest
```

Some tests may require the model checkpoint or other local assets that are intentionally not tracked in Git.

## Current Scope and Limitations

- The current model performs **single-image Pokémon classification**; it is not a YOLO-style detector and does not draw bounding boxes around multiple Pokémon.
- Confidence is a model score, not a guarantee of correctness.
- PokéAPI access requires an internet connection.
- Model weights and datasets are not included in the repository.
- Complex backgrounds can affect dominant-color extraction.

## Future Roadmap

These extensions belong to the original project vision and should be considered planned until implemented and tested:

- Camera capture in addition to image upload
- Detection history
- More robust foreground/background removal
- Multiple-Pokémon detection with YOLO and bounding boxes
- A lightweight MobileNetV3 model for comparison or lower-resource inference
- Docker and Docker Compose packaging
- GitHub Actions CI/CD
- Cloud deployment, potentially using AWS for the frontend and backend

## Key Design Principle

**The model identifies the Pokémon, PokéAPI supplies its facts, image-color extraction informs the palette, and React presents the investigation.**

## Acknowledgements

- Pokémon data is retrieved from [PokéAPI](https://pokeapi.co/).
- Pokémon names and character artwork belong to their respective owners. This is an independent fan project and is not affiliated with or endorsed by Nintendo, Game Freak, or The Pokémon Company.

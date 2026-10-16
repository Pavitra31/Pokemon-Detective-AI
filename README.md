# Pokémon Detective AI

An AI-powered Pokémon recognition web application built with **React, Flask, and PyTorch**. Upload a Pokémon image to receive a model prediction and explore Pokémon information through PokéAPI.

## Features

- Pokémon image upload and classification
- Prediction confidence scores
- Pokémon information retrieved from PokéAPI
- Dominant image color detection
- Pokémon details, stats, and abilities
- React-based interface with animated interactions
- Flask REST API
- Input validation and API error handling

## Technology Stack

**Frontend**
- React
- Vite
- Tailwind CSS
- Framer Motion
- Lucide React

**Backend**
- Python
- Flask and Flask-CORS
- PyTorch and Torchvision
- Pillow
- Requests

**Model**
- EfficientNet-B0
- 1,012 Pokémon classes
- 224 × 224 image input

**External API**
- [PokéAPI](https://pokeapi.co/)

## Project Structure

```text
Pokemon-Detective-AI/
├── backend/
│   ├── app.py
│   └── services/
│       ├── prediction_service.py
│       └── ...
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── tests/
├── models/
│   └── pokemon_efficientnet_b0_1012_fulltrained.pth
├── datasets/
├── requirements.txt
└── README.md
```

The dataset and model weights are excluded from Git to avoid committing large files.

## Prerequisites

- Python 3.10 or a compatible Python version
- Node.js and npm
- Git
- A trained model checkpoint for image predictions

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Pokemon-Detective-AI.git
cd Pokemon-Detective-AI
```

Replace `YOUR_USERNAME` with your GitHub username and use your actual repository URL.

### 2. Set up the Python backend

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

### 3. Add the trained model

Create the `models` directory if it does not exist, then place the trained checkpoint at:

```text
models/pokemon_efficientnet_b0_1012_fulltrained.pth
```

The model checkpoint is not included in this repository. The prediction endpoint requires it to perform image classification.

### 4. Install frontend dependencies

Open a terminal in the project root and run:

```powershell
cd frontend
npm install
```

## Running the Application

Run the backend and frontend in separate terminals.

### Backend

From the project root, with the Python virtual environment activated:

```powershell
python -m backend.app
```

The Flask backend should be available at:

```text
http://127.0.0.1:5000
```

### Frontend

In another terminal:

```powershell
cd frontend
npm run dev
```

Open the local URL printed by Vite, normally:

```text
http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Backend root endpoint |
| GET | `/api/health` | Health check |
| GET | `/api/pokemon/<name>` | Retrieve Pokémon information |
| POST | `/api/predict` | Predict a Pokémon from an uploaded image |

For image prediction, send a multipart form request with the image under the field expected by the backend implementation.

## Testing

Run the API tests from the project root:

```powershell
python -m pytest tests/test_api.py -v
```

Additional project validation scripts include:

```powershell
python -m tests.test_dataset
python -m tests.test_model
python -m tests.test_prediction
```

The prediction test requires the trained checkpoint and appropriate test image data.

## Model and Dataset Notes

The training dataset manifest contains **59,534 images across 1,012 classes**, split into 47,627 training images and 11,907 validation images.

The full-trained checkpoint achieved the following validation results in the recorded five-epoch run:

- **Top-1 accuracy:** 62.96%
- **Top-5 accuracy:** 78.37%

These are validation results, not a guarantee of accuracy for every uploaded image. Performance may vary depending on image quality, background, pose, and similarity between Pokémon.

Dataset files and model weights are excluded from version control. Ensure you have the required files locally before running model-dependent features.

## Building the Frontend

To create a production frontend build:

```powershell
cd frontend
npm run build
```

To run the frontend linter:

```powershell
npm run lint
```

## Limitations

- Predictions depend on the availability of the trained model checkpoint.
- Prediction confidence is the model's score, not a guarantee that the prediction is correct.
- Pokémon details depend on the external PokéAPI service.
- The project is intended for educational and demonstration purposes.

## Disclaimer

Pokémon and related names and characters are the property of their respective owners. This is an independent educational project and is not affiliated with or endorsed by Nintendo, Game Freak, or The Pokémon Company.

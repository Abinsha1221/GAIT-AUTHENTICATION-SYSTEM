import os

# Get the folder where this script runs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder where you put the 3 model files I sent you
ASSETS_DIR = os.path.join(BASE_DIR, 'model_assets')

# Paths to specific files
MODEL_PATH = os.path.join(ASSETS_DIR, 'tower_model_phase2.keras')
SCALER_PATH = os.path.join(ASSETS_DIR, 'scaler.joblib')
DB_PATH = os.path.join(ASSETS_DIR, 'gallery_embeddings.pkl')

# --- ⚡ THE MAGIC FIX ---
# We force every video to pretend it is this resolution.
# This makes the Scaler work for ANY camera (webcam, phone, etc).
OUMVLP_WIDTH = 1280.0
OUMVLP_HEIGHT = 980.0

# Security Threshold (Based on our earlier testing)
# Distance < 0.115 means it's the same person.
SECURITY_THRESHOLD = 0.115
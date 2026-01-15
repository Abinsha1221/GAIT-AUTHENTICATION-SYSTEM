import cv2
import numpy as np
import joblib
import pickle
import os

# Fix for OneDNN warning
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf

# --- IMPORTANT CHANGES HERE ---
import keras
from keras.models import load_model
from keras.initializers import Orthogonal  # <--- YOU ARE MISSING THIS
# ------------------------------

import config
import mediapipe as mp

# Initialize MediaPipe Pose (LOCAL SAFE)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


class GaitSystem:
    def __init__(self):
        print("⏳ Loading AI Models... (This might take 10 seconds)")
        
        # 1. Load the Scaler (The Ruler)
        if not os.path.exists(config.SCALER_PATH):
            raise FileNotFoundError(f"Missing {config.SCALER_PATH}")
        self.scaler = joblib.load(config.SCALER_PATH)
        
        # 2. Load the Neural Network (The Brain)
        if not os.path.exists(config.MODEL_PATH):
            raise FileNotFoundError(f"Missing {config.MODEL_PATH}")
        
        # --- CHANGE THIS LINE ---
        self.model = load_model(
            config.MODEL_PATH, 
            compile=False,
            custom_objects={'Orthogonal': Orthogonal}  # <--- ADD THIS
        )
        
        # 3. Load the User Database
        self.gallery = {}
        if os.path.exists(config.DB_PATH):
            with open(config.DB_PATH, 'rb') as f:
                self.gallery = pickle.load(f)
            print(f"✅ Database loaded: {len(self.gallery)} users found.")
        else:
            print("⚠️ No database found. A new one will be created upon registration.")

    def extract_skeleton(self, frame):
        """
        Extracts 18 joints and applies the CRITICAL 1280x980 SCALING.
        """
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks: return None
        lm = results.pose_landmarks.landmark
        
        # --- THE MAGIC FIX IS HERE ---
        # We multiply by fixed OUMVLP dimensions, NOT the actual video size.
        def get_xy(idx):
            return [lm[idx].x * config.OUMVLP_WIDTH, lm[idx].y * config.OUMVLP_HEIGHT]
        
        # Map MediaPipe(33) to OpenPose(18)
        kp_nose = get_xy(0)
        s1, s2 = get_xy(11), get_xy(12)
        kp_neck = [(s1[0]+s2[0])/2, (s1[1]+s2[1])/2] # Calculate Neck
        
        kp_r_arm = [get_xy(12), get_xy(14), get_xy(16)]
        kp_l_arm = [get_xy(11), get_xy(13), get_xy(15)]
        kp_r_leg = [get_xy(24), get_xy(26), get_xy(28)]
        kp_l_leg = [get_xy(23), get_xy(25), get_xy(27)]
        kp_face = [get_xy(5), get_xy(2), get_xy(8), get_xy(7)]
        
        # Flatten to 1D array of 36 numbers
        return np.array([kp_nose, kp_neck] + kp_r_arm + kp_l_arm + kp_r_leg + kp_l_leg + kp_face).flatten()

    def process_video_to_embedding(self, video_path):
        """Reads video -> Extracts Skeleton -> Normalizes -> Returns Embedding"""
        cap = cv2.VideoCapture(video_path)
        frames_data = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            skel = self.extract_skeleton(frame)
            if skel is not None: frames_data.append(skel)
        cap.release()
        
        if len(frames_data) < 10: 
            print("❌ Video too short or no skeleton detected.")
            return None
        
        # Resample to exactly 24 frames
        indices = np.linspace(0, len(frames_data) - 1, 24).astype(int)
        resampled = np.array([frames_data[i] for i in indices])
        
        # Normalize using the Scaler
        normalized = self.scaler.transform(resampled)
        sequence = normalized.reshape(1, 24, 36)
        
        # Get Embedding from Model
        return self.model.predict(sequence, verbose=0)[0]

    def authenticate_user(self, video_path):
        """Compares the uploaded video against the database."""
        live_emb = self.process_video_to_embedding(video_path)
        
        if live_emb is None:
            return {"authenticated": False, "error": "Could not detect a person in the video"}

        best_score = float('inf')
        best_user = None
        
        # Compare against every user in the database
        for name, stored_embeddings in self.gallery.items():
            # Calculate distance to all stored videos of this user
            distances = [np.linalg.norm(live_emb - saved) for saved in stored_embeddings]
            avg_dist = np.mean(distances)
            
            if avg_dist < best_score:
                best_score = avg_dist
                best_user = name
        
        print(f"🔍 Closest Match: {best_user} with score {best_score:.4f}")

        # Check Threshold
        if best_score < config.SECURITY_THRESHOLD:
            return {"authenticated": True, "user_id": best_user, "score": float(best_score)}
        else:
            return {"authenticated": False, "details": "Gait mismatch", "score": float(best_score)}

    def register_user(self, name, video_path):
        """Adds a new user to the database."""
        emb = self.process_video_to_embedding(video_path)
        
        if emb is None:
            return False
        
        if name not in self.gallery:
            self.gallery[name] = []
        
        self.gallery[name].append(emb)
        
        # Save updated database to disk
        with open(config.DB_PATH, 'wb') as f:
            pickle.dump(self.gallery, f)
            
        return True
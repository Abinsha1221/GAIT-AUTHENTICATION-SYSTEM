from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from processor import GaitSystem

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Create temporary folder for video uploads
UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the AI
gait_system = GaitSystem()

@app.route('/register', methods=['POST'])
def register():
    # 1. Check if files exist
    if 'gait_video' not in request.files or 'user_id' not in request.form:
        return jsonify({"error": "Missing video or name"}), 400
    
    video = request.files['gait_video']
    user_id = request.form['user_id']
    
    # 2. Save video temporarily
    temp_path = os.path.join(UPLOAD_FOLDER, f"reg_{user_id}.mp4")
    video.save(temp_path)
    
    # 3. Process Registration
    try:
        success = gait_system.register_user(user_id, temp_path)
        if success:
            return jsonify({"user_id": user_id, "message": "User registered successfully"})
        else:
            return jsonify({"error": "Failed to process video. Ensure full body is visible."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    # 1. Check file
    if 'gait_video' not in request.files:
        return jsonify({"error": "No video uploaded"}), 400
    
    video = request.files['gait_video']
    temp_path = os.path.join(UPLOAD_FOLDER, "auth_temp.mp4")
    video.save(temp_path)
    
    # 2. Process Authentication
    try:
        result = gait_system.authenticate_user(temp_path)
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Server processing error"}), 500
    finally:
        # Clean up file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(debug=True, port=5000)
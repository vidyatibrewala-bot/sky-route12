from flask import Flask, request, jsonify
from flask_cors import CORS
from stable_baselines3 import PPO
from drone_env import DroneAidEnv
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Load the trained model
MODEL_PATH = "ppo_drone_aid.zip"
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "ppo_drone_30x30.zip"

if os.path.exists(MODEL_PATH):
    model = PPO.load(MODEL_PATH)
    print(f"Model loaded: {MODEL_PATH}")
else:
    model = None
    print("Warning: No model found. Predictions will be random.")

# Initialize the environment
env = DroneAidEnv()

@app.route('/reset', methods=['POST'])
def reset():
    """Endpoint for OpenEnv Reset"""
    obs, info = env.reset()
    return jsonify({
        "observation": obs.tolist(),
        "info": info,
        "status": "reset successful"
    })

@app.route('/step', methods=['POST'])
def step():
    """Endpoint for OpenEnv Step"""
    data = request.json
    action = data.get('action')
    
    if action is None:
        return jsonify({"error": "Missing action"}), 400
        
    obs, reward, terminated, truncated, info = env.step(action)
    return jsonify({
        "observation": obs.tolist(),
        "reward": float(reward),
        "done": bool(terminated or truncated),
        "info": info
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Legacy endpoint for UI compatibility"""
    data = request.json
    try:
        obs = np.array([
            float(data['drone_x']), float(data['drone_y']),
            float(data['target_x']), float(data['target_y']),
            float(data['battery']), float(data['urgency'])
        ], dtype=np.float32)
        
        if model:
            action, _ = model.predict(obs, deterministic=True)
            act_val = int(action.item()) if hasattr(action, 'item') else int(action)
        else:
            act_val = int(np.random.randint(0, 4))
            
        return jsonify({"action": act_val})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ready", 
        "model_loaded": (model is not None),
        "framework": "OpenEnv-Ready"
    })

if __name__ == '__main__':
    # Default port for Hugging Face Spaces is 7860
    app.run(host='0.0.0.0', port=7860)


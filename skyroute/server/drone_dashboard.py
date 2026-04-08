import os
import numpy as np
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from stable_baselines3 import PPO
from pydantic import BaseModel
from .drone_env import DroneAidEnv

# Load the trained model
MODEL_PATH = "ppo_drone_aid.zip"
if os.path.exists(MODEL_PATH):
    try:
        model = PPO.load(MODEL_PATH)
        print(f"Model loaded successfully: {MODEL_PATH}")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None
else:
    print(f"Warning: {MODEL_PATH} not found. Running in simulation mode (random actions).")
    model = None

# Initialize the Gymnasium environment for OpenEnv compliance
env = DroneAidEnv()


# Define request schema for better validation
class PredictionRequest(BaseModel):
    drone_x: float
    drone_y: float
    target_x: float
    target_y: float
    battery: float
    urgency: float

# Prediction Logic function
def get_prediction(data):
    try:
        drone_pos = [data['drone_x'], data['drone_y']]
        target_pos = [data['target_x'], data['target_y']]
        battery = data['battery']
        urgency = data['urgency']
        
        obs = np.array([
            float(drone_pos[0]), float(drone_pos[1]),
            float(target_pos[0]), float(target_pos[1]),
            float(battery), float(urgency)
        ], dtype=np.float32)
        
        if model:
            action, _ = model.predict(obs, deterministic=True)
            return int(action.item()) if hasattr(action, 'item') else int(action)
        else:
            # Smart fallback: navigate toward target using greedy pathfinding
            dx = target_pos[0] - drone_pos[0]
            dy = target_pos[1] - drone_pos[1]
            
            # Add slight randomness (10% chance) for natural-looking movement
            if np.random.random() < 0.1:
                return int(np.random.randint(0, 4))
            
            # Choose the axis with the largest gap first
            if abs(dx) >= abs(dy):
                # Move along X axis: 0 = X-1(up), 1 = X+1(down)
                return 0 if dx < 0 else 1
            else:
                # Move along Y axis: 2 = Y-1(left), 3 = Y+1(right)
                return 2 if dy < 0 else 3
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0

# Initialize FastAPI app directly (no Gradio wrapper needed)
app = FastAPI(title="SkyRoute AI Command Center")

@app.post("/predict")
async def predict_endpoint(data: dict = Body(...)):
    if not data:
        return {"action": 0, "error": "Missing input data"}
    
    action = get_prediction(data)
    return {"action": action}

@app.post("/reset")
async def reset_endpoint():
    """Endpoint for OpenEnv Reset"""
    obs, info = env.reset()
    return {
        "observation": obs.tolist(),
        "info": info,
        "status": "reset successful"
    }

@app.post("/step")
async def step_endpoint(data: dict = Body(...)):
    """Endpoint for OpenEnv Step"""
    action = data.get('action')
    if action is None:
        return JSONResponse(content={"error": "Missing action"}, status_code=400)
        
    obs, reward, terminated, truncated, info = env.step(action)
    return {
        "observation": obs.tolist(),
        "reward": float(reward),
        "done": bool(terminated or truncated),
        "info": info
    }

@app.get("/health")
async def health_endpoint():
    """Hugging Face & OpenEnv Health Check"""
    return {
        "status": "ready",
        "model_loaded": (model is not None),
        "framework": "OpenEnv-Ready"
    }

# Base directory for absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mount the entire frontend folder at the ROOT (/)
# This serves the dashboard HTML/CSS/JS as the primary UI
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

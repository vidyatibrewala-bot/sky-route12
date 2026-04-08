import os
import sys
import numpy as np
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Defensive imports — if any optional library fails, server still starts
# ---------------------------------------------------------------------------
try:
    from stable_baselines3 import PPO
    _SB3_AVAILABLE = True
except Exception as _sb3_err:
    print(f"[WARNING] stable-baselines3 not available: {_sb3_err}")
    PPO = None
    _SB3_AVAILABLE = False

try:
    from .drone_env import DroneAidEnv
    _ENV_OK = True
except Exception as _env_err:
    print(f"[WARNING] Could not import DroneAidEnv: {_env_err}")
    DroneAidEnv = None
    _ENV_OK = False

# ---------------------------------------------------------------------------
# Load the trained model (non-fatal if missing)
# ---------------------------------------------------------------------------
model = None
if PPO is not None:
    MODEL_PATH = "ppo_drone_aid.zip"
    if os.path.exists(MODEL_PATH):
        try:
            model = PPO.load(MODEL_PATH)
            print(f"[OK] Model loaded: {MODEL_PATH}")
        except Exception as _ml_err:
            print(f"[WARNING] Failed to load model: {_ml_err}")
    else:
        print(f"[WARNING] {MODEL_PATH} not found – using simulation mode.")

# ---------------------------------------------------------------------------
# Initialize the Gymnasium environment for OpenEnv compliance (non-fatal)
# ---------------------------------------------------------------------------
env = None
if DroneAidEnv is not None:
    try:
        env = DroneAidEnv()
        print("[OK] DroneAidEnv initialized.")
    except Exception as _init_err:
        print(f"[WARNING] DroneAidEnv init failed: {_init_err}")

# ---------------------------------------------------------------------------
# Prediction Logic
# ---------------------------------------------------------------------------
def get_prediction(data):
    try:
        drone_pos = [data['drone_x'], data['drone_y']]
        target_pos = [data['target_x'], data['target_y']]

        obs = np.array([
            float(drone_pos[0]), float(drone_pos[1]),
            float(target_pos[0]), float(target_pos[1]),
            float(data.get('battery', 500.0)),
            float(data.get('urgency', 0.0))
        ], dtype=np.float32)

        if model is not None:
            action, _ = model.predict(obs, deterministic=True)
            return int(action.item()) if hasattr(action, 'item') else int(action)

        # Greedy fallback – move toward target
        dx = target_pos[0] - drone_pos[0]
        dy = target_pos[1] - drone_pos[1]
        if np.random.random() < 0.1:
            return int(np.random.randint(0, 4))
        if abs(dx) >= abs(dy):
            return 0 if dx < 0 else 1
        else:
            return 2 if dy < 0 else 3
    except Exception as e:
        print(f"[ERROR] Prediction error: {e}")
        return 0


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(title="SkyRoute AI Command Center")


@app.get("/health")
async def health_endpoint():
    """Hugging Face & OpenEnv Health Check"""
    return {
        "status": "ready",
        "model_loaded": model is not None,
        "env_ready": env is not None,
        "framework": "OpenEnv-Ready",
    }


@app.post("/reset")
async def reset_endpoint():
    """OpenEnv Reset – MUST return observation + info."""
    if env is None:
        return JSONResponse(
            content={"error": "Environment not initialized"},
            status_code=503,
        )
    try:
        obs, info = env.reset()
        return {
            "observation": obs.tolist(),
            "info": info if info else {},
        }
    except Exception as e:
        print(f"[ERROR] /reset failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/step")
async def step_endpoint(data: dict = Body(...)):
    """OpenEnv Step"""
    if env is None:
        return JSONResponse(
            content={"error": "Environment not initialized"},
            status_code=503,
        )
    action = data.get("action")
    if action is None:
        return JSONResponse(content={"error": "Missing action"}, status_code=400)
    try:
        obs, reward, terminated, truncated, info = env.step(action)
        return {
            "observation": obs.tolist(),
            "reward": float(reward),
            "done": bool(terminated or truncated),
            "info": info if info else {},
        }
    except Exception as e:
        print(f"[ERROR] /step failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/predict")
async def predict_endpoint(data: dict = Body(...)):
    if not data:
        return {"action": 0, "error": "Missing input data"}
    action = get_prediction(data)
    return {"action": action}


# ---------------------------------------------------------------------------
# Mount static frontend LAST so API routes always take priority
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
    print(f"[OK] Frontend mounted from: {FRONTEND_DIR}")
else:
    print(f"[WARNING] Frontend dir not found: {FRONTEND_DIR}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

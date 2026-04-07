import os
import numpy as np
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from stable_baselines3 import PPO
import gradio as gr

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
            return int(np.random.randint(0, 4))
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0

# Create Gradio Blocks app
# We use Gradio's internal FastAPI app to add our custom /predict endpoint
with gr.Blocks(title="SkyRoute AI Command Center", theme=gr.themes.Soft()) as demo:
    # Embed the custom dashboard
    # Note: On Hugging Face, the static files will be served from /dashboard
    gr.HTML("""
        <div style="width: 100%; height: 100vh; overflow: hidden; margin: 0; padding: 0;">
            <iframe src="/dashboard" 
                    style="width: 100%; height: 100%; border: none;" 
                    title="SkyRoute Dashboard">
            </iframe>
        </div>
    """)

# Access the FastAPI app from Gradio
app = demo.app = FastAPI()

@app.post("/predict")
async def predict_endpoint(request: Request):
    data = await request.json()
    action = get_prediction(data)
    return {"action": action}

# Mount the entire frontend folder so index.html can find style.css and app.js
app.mount("/dashboard", StaticFiles(directory="frontend", html=True), name="dashboard")

# Override the root to serve our dashboard directly or just let Gradio handle it
# Actually, the simplest way is to point the iframe to /frontend/index.html
# and have app.js fetch from /predict

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

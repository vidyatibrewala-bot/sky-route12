import sys
import os
from stable_baselines3 import PPO
from drone_env import DroneAidEnv
import numpy as np

def run_inference():
    print("[START] Drone Inference Session")
    
    # Load model
    model_path = "ppo_drone_aid.zip"
    if not os.path.exists(model_path):
        model_path = "ppo_drone_30x30.zip"
        
    print(f"[STEP] Loading model from {model_path}")
    if os.path.exists(model_path):
        model = PPO.load(model_path)
    else:
        model = None
        print("[WARNING] No model found, using random actions")

    # Initialize env
    env = DroneAidEnv()
    obs, info = env.reset()
    
    print(f"[STEP] Initial Observation: {obs.tolist()}")
    
    # Perform one sample prediction
    if model:
        action, _ = model.predict(obs, deterministic=True)
        act_val = int(action.item())
    else:
        act_val = int(np.random.randint(0, 4))
        
    print(f"[STEP] Predicted Action: {act_val}")
    
    # Take a step
    obs, reward, done, truncated, info = env.step(act_val)
    print(f"[STEP] Reward: {reward}, Done: {done}")
    
    print("[END] Inference Complete")

if __name__ == "__main__":
    run_inference()


"""
SkyRoute Drone AI - Inference Script
Runs a trained PPO agent in a drone delivery environment.
This script is the entry point for OpenEnv validation.
"""

import sys
import os
import traceback
from openai import OpenAI
import json

def run_inference():
    """Main inference function for drone navigation."""
    try:
        print("[START] SkyRoute Drone Inference Session")
        # Initialize OpenAI client for LiteLLM proxy
        client = OpenAI(
            base_url=os.environ["API_BASE_URL"],
            api_key=os.environ["API_KEY"]
        )

        # Import dependencies with error handling
        try:
            import numpy as np
        except ImportError:
            print("[ERROR] numpy not installed")
            sys.exit(1)

        try:
            from stable_baselines3 import PPO
        except ImportError:
            print("[WARNING] stable-baselines3 not installed, using random actions")
            PPO = None

        # Import the drone environment
        # Try multiple import paths for compatibility
        DroneAidEnv = None
        try:
            from server.drone_env import DroneAidEnv
            print("[STEP] Imported DroneAidEnv from server.drone_env")
        except ImportError:
            pass

        if DroneAidEnv is None:
            try:
                from drone_env import DroneAidEnv
                print("[STEP] Imported DroneAidEnv from drone_env")
            except ImportError:
                pass

        if DroneAidEnv is None:
            # Inline minimal environment as fallback
            print("[WARNING] Could not import DroneAidEnv, using inline fallback")
            import gymnasium as gym
            from gymnasium import spaces

            class DroneAidEnv(gym.Env):
                metadata = {"render_modes": ["ansi", "human"]}

                def __init__(self, render_mode=None):
                    super().__init__()
                    self.render_mode = render_mode
                    self.grid_size = 30
                    self.observation_space = spaces.Box(
                        low=np.array([0, 0, 0, 0, 0.0, 0.0], dtype=np.float32),
                        high=np.array([29, 29, 29, 29, 500.0, 1.0], dtype=np.float32),
                        dtype=np.float32
                    )
                    self.action_space = spaces.Discrete(4)
                    self._action_to_direction = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}

                def reset(self, seed=None, options=None):
                    super().reset(seed=seed)
                    self.battery = 500.0
                    self.urgency = float(self.np_random.choice([0.0, 1.0]))
                    self.drone_pos = (int(self.np_random.integers(0, self.grid_size)),
                                      int(self.np_random.integers(0, self.grid_size)))
                    self.target_pos = (int(self.np_random.integers(0, self.grid_size)),
                                       int(self.np_random.integers(0, self.grid_size)))
                    self.obstacles = set()
                    num_obstacles = int(self.np_random.integers(15, 26))
                    while len(self.obstacles) < num_obstacles:
                        o = (int(self.np_random.integers(0, self.grid_size)),
                             int(self.np_random.integers(0, self.grid_size)))
                        if o != self.drone_pos and o != self.target_pos:
                            self.obstacles.add(o)
                    self.done = False
                    return self._get_obs(), {}

                def _get_obs(self):
                    return np.array([
                        float(self.drone_pos[0]), float(self.drone_pos[1]),
                        float(self.target_pos[0]), float(self.target_pos[1]),
                        float(self.battery), float(self.urgency)
                    ], dtype=np.float32)

                def step(self, action):
                    act = int(action.item()) if isinstance(action, (np.ndarray, np.generic)) else int(action)
                    direction = self._action_to_direction[act]
                    new_pos = (
                        int(np.clip(self.drone_pos[0] + direction[0], 0, self.grid_size - 1)),
                        int(np.clip(self.drone_pos[1] + direction[1], 0, self.grid_size - 1))
                    )
                    cost = 2.0 if self.urgency == 1.0 else 1.0
                    self.battery = max(0.0, self.battery - cost)
                    self.drone_pos = new_pos
                    reward = -0.1
                    terminated = False
                    if self.battery <= 0 or self.drone_pos in self.obstacles:
                        reward = -500.0
                        terminated = True
                    elif self.drone_pos == self.target_pos:
                        reward = 1000.0 + (self.battery * 2)
                        terminated = True
                    self.done = terminated
                    return self._get_obs(), float(reward), terminated, False, {}

                def render(self):
                    pass

        # Load model
        model = None
        model_paths = ["ppo_drone_aid.zip", "ppo_drone_30x30.zip"]
        if PPO is not None:
            for mp in model_paths:
                if os.path.exists(mp):
                    try:
                        model = PPO.load(mp)
                        print(f"[STEP] Model loaded: {mp}")
                        break
                    except Exception as e:
                        print(f"[WARNING] Failed to load {mp}: {e}")
            if model is None:
                print("[WARNING] No model found, using greedy navigation")

        # Initialize environment
        env = DroneAidEnv()
        obs, info = env.reset()
        print(f"[STEP] Environment initialized")
        print(f"[STEP] Initial Observation: {obs.tolist()}")
        # Analyze scenario with LLM via LiteLLM proxy
        def analyze_scenario_with_llm(obs_list):
            """Send observation to LLM and return analysis string."""
            prompt = (
                "You are an AI assisting a drone navigation simulation. "
                f"Current observation: {obs_list}. "
                "Provide a concise analysis of battery level, urgency, and distance to target."
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[WARNING] LLM call failed: {e}")
                return ""
        llm_analysis = analyze_scenario_with_llm(obs.tolist())
        if llm_analysis:
            print(f"[LLM] {llm_analysis}")

        # Run inference loop
        total_reward = 0.0
        max_steps = 200
        for step_num in range(max_steps):
            if model is not None:
                action, _ = model.predict(obs, deterministic=True)
                act_val = int(action.item()) if hasattr(action, 'item') else int(action)
            else:
                # Greedy fallback: move toward target
                drone_x, drone_y = obs[0], obs[1]
                target_x, target_y = obs[2], obs[3]
                dx = target_x - drone_x
                dy = target_y - drone_y
                if abs(dx) >= abs(dy):
                    act_val = 0 if dx < 0 else 1
                else:
                    act_val = 2 if dy < 0 else 3

            obs, reward, done, truncated, info = env.step(act_val)
            total_reward += reward

            if step_num % 50 == 0:
                print(f"[STEP {step_num}] Action: {act_val}, Reward: {reward:.2f}, Total: {total_reward:.2f}")

            if done or truncated:
                print(f"[STEP {step_num}] Episode ended. Final reward: {total_reward:.2f}")
                break

        print(f"[RESULT] Total Reward: {total_reward:.2f}")
        print("[END] Inference Complete")

    except Exception as e:
        print(f"[ERROR] Unhandled exception in inference: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_inference()

from fastapi import FastAPI, HTTPException
from email_env import EmailTriageEnv, Action, Observation, State
from typing import Dict
import uuid

app = FastAPI(title="Email Triage OpenEnv API")

# Store sessions in memory for this demo
sessions: Dict[str, EmailTriageEnv] = {}

@app.post("/reset")
def reset(session_id: str = "default") -> Observation:
    env = EmailTriageEnv()
    sessions[session_id] = env
    return env.reset()

@app.post("/step")
def step(action: Action, session_id: str = "default") -> dict:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Call /reset first.")
    
    env = sessions[session_id]
    obs, reward, done, info = env.step(action)
    
    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state(session_id: str = "default") -> State:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    return sessions[session_id].state()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

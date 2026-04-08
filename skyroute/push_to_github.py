"""
Push all needed files to GitHub repo root using GitHub REST API.
This script reads local files and pushes them to the GitHub repo
so the validator can find inference.py at the root level.
"""

import requests
import base64
import os
import json

# Configuration - update these values
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # Set your token
REPO_OWNER = "vidyatibrewala-bot"
REPO_NAME = "sky-route12"
BRANCH = "main"

API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file_sha(path):
    """Get the SHA of an existing file (needed for updates)."""
    r = requests.get(f"{API_BASE}/contents/{path}?ref={BRANCH}", headers=headers)
    if r.status_code == 200:
        return r.json().get("sha")
    return None

def push_file(local_path, remote_path, message):
    """Push a single file to the GitHub repo."""
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    
    sha = get_file_sha(remote_path)
    payload = {
        "message": message,
        "content": content,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha  # Update existing file
    
    r = requests.put(f"{API_BASE}/contents/{remote_path}", headers=headers, json=payload)
    if r.status_code in (200, 201):
        print(f"✅ Pushed: {remote_path}")
    else:
        print(f"❌ Failed: {remote_path} - {r.status_code}: {r.json().get('message', '')}")
    return r.status_code in (200, 201)

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("ERROR: Set the GITHUB_TOKEN environment variable first!")
        print("Run: $env:GITHUB_TOKEN = 'your_github_personal_access_token'")
        exit(1)
    
    # Files to push to the repo root
    files_to_push = [
        ("inference.py", "inference.py", "Add inference.py to repo root for validator"),
        ("drone_env.py", "drone_env.py", "Add drone_env.py to repo root"),
        ("requirements.txt", "requirements.txt", "Add requirements.txt to repo root"),
        ("openenv.yaml", "openenv.yaml", "Add openenv.yaml to repo root"),
        ("Dockerfile", "Dockerfile", "Add Dockerfile to repo root"),
        ("README.md", "README.md", "Update README.md at repo root"),
        ("ppo_drone_aid.zip", "ppo_drone_aid.zip", "Add model to repo root"),
    ]
    
    # Also push server files
    server_files = [
        ("server/__init__.py", "server/__init__.py", "Add server package init"),
        ("server/app.py", "server/app.py", "Add server app"),
        ("server/drone_dashboard.py", "server/drone_dashboard.py", "Add drone dashboard"),
        ("server/drone_env.py", "server/drone_env.py", "Add server drone env"),
    ]
    
    all_files = files_to_push + server_files
    
    success = 0
    fail = 0
    for local, remote, msg in all_files:
        local_path = os.path.join(r"c:\Users\HP\Downloads\skyroute", local)
        if os.path.exists(local_path):
            if push_file(local_path, remote, msg):
                success += 1
            else:
                fail += 1
        else:
            print(f"⚠️ Skipped (not found): {local}")
    
    print(f"\nDone! {success} pushed, {fail} failed")

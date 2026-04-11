from huggingface_hub import HfApi
import os

token = os.environ.get("HF_TOKEN", "your_token_here")
repo_id = "happyjourney1/skyroute-dashboard"
api = HfApi()
# Ensure the Space repo exists (create if missing)
try:
    api.create_repo(repo_id=repo_id, repo_type="space", token=token, space_sdk="docker", exist_ok=True)
    print(f"Space repository {repo_id} is ready.")
except Exception as e:
    print(f"Failed to ensure repo exists: {e}")

print(f"Uploading files to {repo_id}...")

try:
    api.upload_folder(
        folder_path=".",
        repo_id=repo_id,
        repo_type="space",
        token=token,
        # Exclude unnecessary files to keep the build clean and secure
        ignore_patterns=[
            "__pycache__/*",
            ".cache/*",
            "*.pyc",
            "upload_script.py",
            "cleanup_remote.py",
            ".env",
            "legacy/*",
            "drone_backup/*",
            ".gitignore",
            "push_to_github.py",
            "temp_github_clone/*",
            "hf_upload.*",
            "skyroute_source/*",
            "scratch/*",
        ]
    )
    print("Upload successful!")
except Exception as e:
    print(f"Upload failed: {e}")

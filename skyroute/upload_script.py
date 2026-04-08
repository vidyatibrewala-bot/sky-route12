from huggingface_hub import HfApi
import os

token = "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"
repo_id = "happyjourney1/skyroute-dashboard"

api = HfApi()

print(f"Uploading files to {repo_id}...")

try:
    api.upload_folder(
        folder_path=".",
        repo_id=repo_id,
        repo_type="space",
        token=token,
        # Exclude unnecessary files to keep the build clean
        ignore_patterns=[
            "__pycache__/*",
            ".cache/*",
            "*.pyc",
            "upload_script.py",
            "cleanup_remote.py",
            ".env",
            "legacy/*",
            "drone_backup/*",
            "uv.lock",
            ".gitignore",
            "push_to_github.py",
            "temp_github_clone/*",
        ]
    )
    print("Upload successful!")
except Exception as e:
    print(f"Upload failed: {e}")

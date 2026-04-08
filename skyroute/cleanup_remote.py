from huggingface_hub import HfApi
import os

token = "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"
repo_id = "happyjourney1/skyroute-dashboard"

api = HfApi()

# Remove old leftover files that should not be on the HF Space
files_to_delete = [
    "inference.py",       # Leftover from email triage project
    "netlify.toml",       # Not needed for HF deployment
    "pyproject.toml",     # Not needed
    "uv.lock",            # Not needed - very large file
]

for file_path in files_to_delete:
    print(f"Deleting {file_path} from {repo_id}...")
    try:
        api.delete_file(
            path_in_repo=file_path,
            repo_id=repo_id,
            repo_type="space",
            token=token
        )
        print(f"Successfully deleted {file_path}")
    except Exception as e:
        print(f"Could not delete {file_path}: {e}")

print("Cleanup complete!")

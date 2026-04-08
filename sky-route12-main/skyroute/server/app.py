import os
import sys

# Ensure the current directory is in the path for imports
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .drone_dashboard import app

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()

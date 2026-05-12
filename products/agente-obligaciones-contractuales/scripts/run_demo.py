from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.ui.gradio_app import launch_demo

if __name__ == "__main__":
    launch_demo()


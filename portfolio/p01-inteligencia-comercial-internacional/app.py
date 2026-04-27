from __future__ import annotations

from pathlib import Path
import runpy


def main() -> None:
    target = Path(__file__).resolve().parent / "app" / "streamlit_app.py"
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()

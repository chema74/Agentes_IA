from __future__ import annotations

import sys


def main() -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit("Falta uvicorn. Instala requirements.txt antes de arrancar el servidor.") from exc
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    sys.exit(main())

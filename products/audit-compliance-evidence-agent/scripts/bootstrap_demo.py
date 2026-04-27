from __future__ import annotations

from pathlib import Path

from core.config.settings import settings
from core.db.repository import STORE
from scripts.seed_mock_data import seed_demo_data


def main() -> None:
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.export_dir).mkdir(parents=True, exist_ok=True)
    seed_demo_data(reset=True)
    print("Demo inicializada.")
    print(f"Scopes cargados: {len(STORE.scopes)}")
    print(f"Controles cargados: {len(STORE.controls)}")
    print(f"Evidencias cargadas: {len(STORE.evidence)}")


if __name__ == "__main__":
    main()

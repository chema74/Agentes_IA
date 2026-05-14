from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "products"
PORTFOLIO_DIR = ROOT / "portfolio"


def _run_pytest(project_dir: Path) -> int:
    cmd = [sys.executable, "-m", "pytest", "-q", "--import-mode=importlib"]
    print(f"RUN  {project_dir.relative_to(ROOT)}")
    return subprocess.run(cmd, cwd=project_dir, check=False).returncode


def _iter_projects(base_dir: Path) -> list[Path]:
    if not base_dir.exists():
        return []
    return sorted(p for p in base_dir.iterdir() if p.is_dir() and (p / "tests").exists())


def main() -> int:
    failures: list[str] = []
    projects = _iter_projects(PRODUCTS_DIR) + _iter_projects(PORTFOLIO_DIR)

    if not projects:
        print("No se encontraron proyectos con tests/.")
        return 1

    for project in projects:
        rc = _run_pytest(project)
        if rc != 0:
            failures.append(str(project.relative_to(ROOT)))

    if failures:
        print("Fallaron tests en:")
        for project in failures:
            print(f"- {project}")
        return 1

    print("Monorepo tests OK (ejecucion aislada por proyecto).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIRS = [ROOT / "portfolio", ROOT / "products"]


def _project_id_from_folder(name: str) -> str | None:
    match = re.match(r"^p(\d+)-", name)
    if not match:
        return None
    return f"P{int(match.group(1)):02d}"


def _get_readme(project_dir: Path) -> Path | None:
    for candidate in ("README.md", "readme.md"):
        p = project_dir / candidate
        if p.exists():
            return p
    return None


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    errors: list[str] = []

    for projects_dir in PROJECTS_DIRS:
        if not projects_dir.exists():
            errors.append(f"No existe el directorio '{projects_dir.name}'.")
            continue

        for project in sorted(p for p in projects_dir.iterdir() if p.is_dir()):
            expected_id = _project_id_from_folder(project.name)
            readme = _get_readme(project)
            if readme is None:
                errors.append(f"{project}: falta README.md/readme.md")
                continue

            content = _read_text(readme)
            first_non_empty = ""
            for line in content.splitlines():
                if line.strip():
                    first_non_empty = line.strip().lstrip("\ufeff")
                    break

            if expected_id and not first_non_empty.startswith(f"# {expected_id}"):
                errors.append(
                    f"{project.name}: encabezado README no alineado "
                    f"(esperado '# {expected_id} ...')."
                )

            if not (project / "requirements.txt").exists():
                errors.append(f"{project.name}: falta requirements.txt")

            has_entrypoint = (
                (project / "app.py").exists()
                or (project / "streamlit_app.py").exists()
                or (project / "app" / "streamlit_app.py").exists()
                or (project / "app" / "main.py").exists()
            )
            if not has_entrypoint:
                errors.append(
                    f"{project.name}: falta entrypoint "
                    f"(app.py, streamlit_app.py, app/streamlit_app.py o app/main.py)"
                )

    if errors:
        print("CI lint detecto inconsistencias:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("CI lint OK: estructura y README coherentes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

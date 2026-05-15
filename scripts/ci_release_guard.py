from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "products"
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def _load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def main() -> int:
    errors: list[str] = []

    if not PRODUCTS_DIR.exists():
        print("No existe el directorio products.")
        return 1

    for product in sorted(p for p in PRODUCTS_DIR.iterdir() if p.is_dir()):
        pyproject = product / "pyproject.toml"
        if not pyproject.exists():
            errors.append(f"{product.name}: falta pyproject.toml")
            continue

        data = _load_toml(pyproject)
        project = data.get("project", {})
        version = str(project.get("version", "")).strip()
        name = str(project.get("name", "")).strip()

        if not name:
            errors.append(f"{product.name}: project.name vacio en pyproject.toml")
        if not version:
            errors.append(f"{product.name}: project.version vacio en pyproject.toml")
        elif not SEMVER_RE.match(version):
            errors.append(f"{product.name}: version invalida '{version}' (usar SemVer X.Y.Z)")

    if errors:
        print("Release guard detecto problemas:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Release guard OK: metadata de versionado consistente en products.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

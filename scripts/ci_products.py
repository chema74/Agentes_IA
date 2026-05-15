from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "products"


def main() -> int:
    if not PRODUCTS_DIR.exists():
        print("No existe el directorio 'products'.")
        return 1

    failures: list[str] = []
    for product in sorted(p for p in PRODUCTS_DIR.iterdir() if p.is_dir()):
        tests_dir = product / "tests"
        if not tests_dir.exists():
            print(f"SKIP {product.name}: no tiene tests/")
            continue

        print(f"RUN  {product.name}")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=product,
            text=True,
        )
        if result.returncode != 0:
            failures.append(product.name)

    if failures:
        print("Fallaron tests de products:")
        for name in failures:
            print(f"- {name}")
        return 1

    print("Products OK: todos los tests por producto pasan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

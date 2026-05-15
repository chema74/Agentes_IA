from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [ROOT / "core", ROOT / "portfolio", ROOT / "products"]
SKIP_PARTS = {
    ".venv",
    "venv",
    ".venv_check",
    "__pycache__",
    ".pytest_cache",
    ".claude",
    ".git",
    "worktrees",
}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def main() -> int:
    failures: list[str] = []
    checked = 0

    for base in TARGET_DIRS:
        if not base.exists():
            continue
        for py_file in base.rglob("*.py"):
            if should_skip(py_file):
                continue
            checked += 1
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as exc:
                failures.append(f"{py_file}: {exc.msg}")

    if failures:
        print("CI smoke detecto errores de compilacion Python:")
        for err in failures:
            print(f"- {err}")
        return 1

    print(f"CI smoke OK: {checked} archivos Python compilados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


COMMANDS: list[list[str]] = [
    [
        sys.executable, "-m", "ruff", "check", "--fix",
        "scripts/ci_lint.py",
        "scripts/ci_smoke.py",
        "scripts/ci_products.py",
        "scripts/ci_quality.py",
        "scripts/ci_release_guard.py",
        "tests/test_projects_minimal.py",
    ],
    [
        sys.executable, "-m", "ruff", "format", "--check",
        "scripts/ci_lint.py",
        "scripts/ci_smoke.py",
        "scripts/ci_products.py",
        "scripts/ci_quality.py",
        "scripts/ci_release_guard.py",
        "tests/test_projects_minimal.py",
    ],
    [sys.executable, "-m", "mypy", "scripts"],
    [sys.executable, "-m", "bandit", "-q", "-r", "scripts", "-s", "B404,B603"],
    [sys.executable, "-m", "bandit", "-q", "-r", "core", "-lll", "-ii", "-s", "B101"],
    [sys.executable, "-m", "coverage", "run", "-m", "pytest", "-q", "tests/test_projects_minimal.py"],
    [sys.executable, "-m", "coverage", "xml", "-o", "coverage.xml"],
    [sys.executable, "-m", "coverage", "report", "--include=tests/test_projects_minimal.py", "--fail-under=25"],
]



def _run(command: list[str]) -> int:
    print(f"RUN  {' '.join(command)}")
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def main() -> int:
    failures: list[str] = []

    for command in COMMANDS:
        rc = _run(command)
        if rc != 0:
            failures.append(" ".join(command))

    if failures:
        print("CI quality detecto fallos:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("CI quality OK: lint, seguridad y cobertura en verde.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

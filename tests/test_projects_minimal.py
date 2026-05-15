from __future__ import annotations

import py_compile
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "portfolio"

PROJECT_CASES = [
    ("p01-inteligencia-comercial-internacional", "P01"),
    ("p02-agente-multi-herramienta", "P02"),
    ("p03-agente-licitaciones", "P03"),
    ("p04-agente-rrhh-candidatos", "P04"),
    ("p05-rag-documentacion-interna", "P05"),
    ("p06-rag-contratos-legales", "P06"),
    ("p07-chatbot-atencion-cliente", "P07"),
    ("p08-rag-normativa-comercio", "P08"),
    ("p09-evaluador-ideas-negocio", "P09"),
    ("p10-dashboard-lenguaje-natural", "P10"),
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _readme_path(project_dir: Path) -> Path:
    for candidate in ("README.md", "readme.md"):
        p = project_dir / candidate
        if p.exists():
            return p
    raise AssertionError(f"Falta README en {project_dir}")


def _requirements_lines(path: Path) -> list[str]:
    lines = []
    for raw in _read_text(path).splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append(line.lower())
    return lines


@pytest.mark.parametrize("folder,expected_id", PROJECT_CASES)
def test_project_entrypoint_exists_and_compiles(folder: str, expected_id: str) -> None:
    project_dir = PROJECTS_DIR / folder
    app_path = project_dir / "app.py"

    assert project_dir.exists(), f"No existe carpeta de proyecto: {folder}"
    assert app_path.exists(), f"Falta app.py en {folder}"

    py_compile.compile(str(app_path), doraise=True)

    readme = _readme_path(project_dir)
    first_non_empty = next(
        (line.strip().lstrip("\ufeff") for line in _read_text(readme).splitlines() if line.strip()),
        "",
    )
    assert first_non_empty.startswith(f"# {expected_id}"), (
        f"README desalineado en {folder}: {first_non_empty}"
    )


@pytest.mark.parametrize("folder,_expected_id", PROJECT_CASES)
def test_project_requirements_have_core_runtime_deps(folder: str, _expected_id: str) -> None:
    req_path = PROJECTS_DIR / folder / "requirements.txt"
    assert req_path.exists(), f"Falta requirements.txt en {folder}"

    reqs = _requirements_lines(req_path)
    assert any(r.startswith("streamlit") for r in reqs), f"{folder} sin Streamlit en requirements"
    assert any(r.startswith("groq") for r in reqs), f"{folder} sin Groq en requirements"

    app_code = _read_text(PROJECTS_DIR / folder / "app.py")
    if "TAVILY_API_KEY" in app_code or "from tavily" in app_code.lower():
        assert any("tavily-python" in r for r in reqs), (
            f"{folder} usa Tavily en app.py pero no lo declara en requirements"
        )


@pytest.mark.parametrize("folder,_expected_id", PROJECT_CASES)
def test_project_env_example_contains_required_keys(folder: str, _expected_id: str) -> None:
    project_dir = PROJECTS_DIR / folder
    env_example = project_dir / ".env.example"
    assert env_example.exists(), f"Falta .env.example en {folder}"

    content = _read_text(env_example)
    assert "GROQ_API_KEY=" in content, f"{folder} sin GROQ_API_KEY en .env.example"

    app_code = _read_text(project_dir / "app.py")
    uses_tavily = "TAVILY_API_KEY" in app_code or "from tavily" in app_code.lower()
    if uses_tavily:
        assert "TAVILY_API_KEY=" in content, (
            f"{folder} usa Tavily pero no define TAVILY_API_KEY en .env.example"
        )

    # Guardrail simple: .env.example no debe incluir claves reales.
    assert not re.search(r"gsk_[A-Za-z0-9]{20,}", content), (
        f"{folder} contiene una GROQ key real en .env.example"
    )
    assert not re.search(r"tvly-[A-Za-z0-9-]{20,}", content), (
        f"{folder} contiene una TAVILY key real en .env.example"
    )

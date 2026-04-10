"""
test_config_loader.py

Fase 18 — Tests de configuración desacoplada.

Cubre:
  - Carga de pesos desde weights.yaml
  - Fallback a defaults cuando el archivo no existe o es inválido
  - Validación de suma de pesos
  - Modo demo: get_demo_result devuelve estructura correcta
  - Modo demo: pais_disponible_en_demo funciona correctamente
  - APP_MODE se resuelve correctamente

Autor: Txema Ríos — CC BY-SA 4.0
"""

import warnings
from pathlib import Path
import tempfile
import textwrap

import pytest

# ---------------------------------------------------------------------------
# Tests: _cargar_weights_yaml (función interna de settings)
# ---------------------------------------------------------------------------

class TestCargarWeightsYaml:
    """Prueba el cargador de weights.yaml en distintos escenarios."""

    def _run_loader(self, yaml_content: str | None) -> dict:
        """
        Auxiliar: ejecuta _cargar_weights_yaml apuntando a un archivo temporal.
        Si yaml_content es None, el archivo no existe.
        """
        from config import settings as s

        # Guardamos la ruta original
        ruta_original = s.WEIGHTS_FILE

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "weights.yaml"

            if yaml_content is not None:
                tmp_path.write_text(yaml_content, encoding="utf-8")
                s.WEIGHTS_FILE = tmp_path
            else:
                # Apuntamos a una ruta que no existe
                s.WEIGHTS_FILE = Path(tmpdir) / "no_existe.yaml"

            try:
                resultado = s._cargar_weights_yaml()
            finally:
                # Restauramos la ruta original siempre
                s.WEIGHTS_FILE = ruta_original

        return resultado

    def test_devuelve_defaults_cuando_archivo_no_existe(self):
        """Si weights.yaml no existe, se devuelven los valores por defecto."""
        resultado = self._run_loader(None)

        assert resultado["scoring"] == pytest.approx(
            {"riesgo_politico": 0.20, "estabilidad_economica": 0.20,
             "riesgo_regulatorio": 0.15, "riesgo_comercial": 0.15,
             "riesgo_geopolitico": 0.10, "riesgo_operativo": 0.10,
             "ajuste_sectorial": 0.05, "oportunidad_sectorial": 0.05},
            abs=1e-6,
        )

    def test_carga_pesos_validos_desde_yaml(self):
        """Pesos válidos en YAML se cargan correctamente."""
        yaml_content = textwrap.dedent("""\
            scoring_weights:
              riesgo_politico:       0.25
              estabilidad_economica: 0.25
              riesgo_regulatorio:    0.10
              riesgo_comercial:      0.10
              riesgo_geopolitico:    0.10
              riesgo_operativo:      0.10
              ajuste_sectorial:      0.05
              oportunidad_sectorial: 0.05
            country_vs_sector_weights:
              score_riesgo_pais:      0.80
              score_riesgo_sectorial: 0.20
            app_mode: "production"
        """)
        resultado = self._run_loader(yaml_content)

        assert resultado["scoring"]["riesgo_politico"] == pytest.approx(0.25, abs=1e-6)
        assert resultado["scoring"]["estabilidad_economica"] == pytest.approx(0.25, abs=1e-6)
        assert resultado["app_mode"] == "production"

    def test_fallback_cuando_pesos_no_suman_uno(self):
        """Si los pesos no suman 1.0, se usan los defaults y se emite warning."""
        yaml_content = textwrap.dedent("""\
            scoring_weights:
              riesgo_politico:       0.50
              estabilidad_economica: 0.50
              riesgo_regulatorio:    0.50
              riesgo_comercial:      0.50
              riesgo_geopolitico:    0.10
              riesgo_operativo:      0.10
              ajuste_sectorial:      0.05
              oportunidad_sectorial: 0.05
        """)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            resultado = self._run_loader(yaml_content)

        # Se debe haber emitido al menos un warning
        assert any("scoring_weights" in str(warning.message) for warning in w)

        # Los pesos deben ser los defaults (no los del YAML inválido)
        from config.settings import _DEFAULT_SCORING_WEIGHTS
        assert resultado["scoring"] == pytest.approx(_DEFAULT_SCORING_WEIGHTS, abs=1e-6)

    def test_carga_modo_demo_desde_yaml(self):
        """Si app_mode es 'demo' en el YAML, se carga como demo."""
        yaml_content = textwrap.dedent("""\
            scoring_weights:
              riesgo_politico:       0.20
              estabilidad_economica: 0.20
              riesgo_regulatorio:    0.15
              riesgo_comercial:      0.15
              riesgo_geopolitico:    0.10
              riesgo_operativo:      0.10
              ajuste_sectorial:      0.05
              oportunidad_sectorial: 0.05
            app_mode: "demo"
        """)
        resultado = self._run_loader(yaml_content)
        assert resultado["app_mode"] == "demo"

    def test_fallback_cuando_yaml_malformado(self):
        """YAML malformado → defaults sin excepción."""
        yaml_content = "esto: no: es: yaml: válido: {{{{{"
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            resultado = self._run_loader(yaml_content)

        from config.settings import _DEFAULT_SCORING_WEIGHTS
        assert resultado["scoring"] == pytest.approx(_DEFAULT_SCORING_WEIGHTS, abs=1e-6)

    def test_fallback_cuando_yaml_no_es_diccionario(self):
        """YAML que no es dict (ej: lista) → defaults con warning."""
        yaml_content = "- item1\n- item2\n"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            resultado = self._run_loader(yaml_content)

        assert any("diccionario válido" in str(warning.message) for warning in w)
        from config.settings import _DEFAULT_SCORING_WEIGHTS
        assert resultado["scoring"] == pytest.approx(_DEFAULT_SCORING_WEIGHTS, abs=1e-6)

    def test_modo_desconocido_usa_production(self):
        """Un app_mode no reconocido → se mantiene 'production' con warning."""
        yaml_content = textwrap.dedent("""\
            scoring_weights:
              riesgo_politico:       0.20
              estabilidad_economica: 0.20
              riesgo_regulatorio:    0.15
              riesgo_comercial:      0.15
              riesgo_geopolitico:    0.10
              riesgo_operativo:      0.10
              ajuste_sectorial:      0.05
              oportunidad_sectorial: 0.05
            app_mode: "staging"
        """)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            resultado = self._run_loader(yaml_content)

        assert any("staging" in str(warning.message) for warning in w)
        assert resultado["app_mode"] == "production"


# ---------------------------------------------------------------------------
# Tests: pesos por defecto son coherentes
# ---------------------------------------------------------------------------

class TestDefaultWeights:
    """Verifica que los pesos por defecto en settings.py son matemáticamente coherentes."""

    def test_scoring_weights_suman_uno(self):
        from config.settings import _DEFAULT_SCORING_WEIGHTS
        total = sum(_DEFAULT_SCORING_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9

    def test_country_vs_sector_weights_suman_uno(self):
        from config.settings import _DEFAULT_COUNTRY_VS_SECTOR_WEIGHTS
        total = sum(_DEFAULT_COUNTRY_VS_SECTOR_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9

    def test_scoring_weights_contienen_8_dimensiones(self):
        from config.settings import _DEFAULT_SCORING_WEIGHTS
        assert len(_DEFAULT_SCORING_WEIGHTS) == 8

    def test_todos_los_pesos_son_positivos(self):
        from config.settings import _DEFAULT_SCORING_WEIGHTS
        for dim, peso in _DEFAULT_SCORING_WEIGHTS.items():
            assert peso > 0, f"El peso de '{dim}' debe ser positivo"


# ---------------------------------------------------------------------------
# Tests: validación runtime mínima
# ---------------------------------------------------------------------------

class TestRuntimeConfiguration:
    """Verifica que la capa de configuración desacoplada no bloquee demo."""

    def test_demo_no_requiere_claves_api(self, monkeypatch):
        from config.settings import validar_configuracion_api

        monkeypatch.setenv("APP_MODE", "demo")
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)

        validar_configuracion_api()

    def test_production_detecta_claves_faltantes(self, monkeypatch):
        from config.settings import validar_configuracion_runtime

        monkeypatch.setenv("APP_MODE", "production")
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)

        faltantes = validar_configuracion_runtime()

        assert faltantes == ["GROQ_API_KEY", "TAVILY_API_KEY"]


# ---------------------------------------------------------------------------
# Tests: modo demo — get_demo_result
# ---------------------------------------------------------------------------

class TestDemoData:
    """Prueba el módulo de datos demo."""

    def test_get_demo_result_devuelve_estructura_correcta(self):
        from domain.demo_data import get_demo_result
        resultado = get_demo_result("México")

        assert isinstance(resultado, dict)
        assert "scores" in resultado
        assert "scores_agregados" in resultado
        assert "resumen_ejecutivo" in resultado
        assert "alertas" in resultado
        assert "oportunidades" in resultado
        assert resultado["_demo_mode"] is True

    def test_get_demo_result_scores_en_rango_valido(self):
        from domain.demo_data import get_demo_result
        resultado = get_demo_result("Alemania")

        for dim, valor in resultado["scores"].items():
            assert 1.0 <= valor <= 10.0, f"Score de {dim} fuera de rango: {valor}"

    def test_get_demo_result_dimensiones_completas(self):
        from domain.demo_data import get_demo_result
        resultado = get_demo_result("Vietnam")

        dimensiones_esperadas = {
            "riesgo_politico", "estabilidad_economica", "riesgo_regulatorio",
            "riesgo_comercial", "riesgo_geopolitico", "riesgo_operativo",
            "ajuste_sectorial", "oportunidad_sectorial",
        }
        assert set(resultado["scores"].keys()) == dimensiones_esperadas

    def test_get_demo_result_scores_agregados_coherentes(self):
        from domain.demo_data import get_demo_result
        resultado = get_demo_result("Australia")

        agregados = resultado["scores_agregados"]
        assert "score_riesgo_pais" in agregados
        assert "score_riesgo_sectorial" in agregados
        assert "score_total" in agregados
        for k, v in agregados.items():
            assert isinstance(v, float), f"{k} debe ser float"
            assert 1.0 <= v <= 10.0, f"{k} fuera de rango: {v}"

    def test_get_demo_result_devuelve_none_para_pais_inexistente(self):
        from domain.demo_data import get_demo_result
        assert get_demo_result("PaisInexistente123") is None

    def test_get_demo_result_insensible_a_mayusculas(self):
        from domain.demo_data import get_demo_result
        resultado = get_demo_result("méxico")
        assert resultado is not None
        assert resultado["_demo_mode"] is True

    def test_pais_disponible_en_demo_true_para_paises_validos(self):
        from domain.demo_data import pais_disponible_en_demo, PAISES_DEMO
        for p in PAISES_DEMO:
            assert pais_disponible_en_demo(p), f"{p} debería estar disponible en demo"

    def test_pais_disponible_en_demo_false_para_desconocido(self):
        from domain.demo_data import pais_disponible_en_demo
        assert pais_disponible_en_demo("PaisDesconocido") is False

    def test_todos_los_paises_demo_devuelven_resultado(self):
        from domain.demo_data import get_demo_result, PAISES_DEMO
        for p in PAISES_DEMO:
            resultado = get_demo_result(p)
            assert resultado is not None, f"get_demo_result('{p}') devolvió None"
            assert resultado.get("_demo_mode") is True

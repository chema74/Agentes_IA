import pytest

from domain.parser import clean_json


def test_clean_json_with_valid_plain_json():
    raw = """
    {
      "pais": "México",
      "resumen_ejecutivo": "País con oportunidades moderadas y algunas cautelas regulatorias.",
      "alertas": ["Riesgo regulatorio", "Inflación moderada", "Dependencia logística"],
      "oportunidades": ["Exportación tecnológica", "Servicios B2B", "Mercado en crecimiento"]
    }
    """

    result = clean_json(raw)

    assert isinstance(result, dict)
    assert result["pais"] == "México"
    assert "resumen_ejecutivo" in result
    assert isinstance(result["alertas"], list)
    assert isinstance(result["oportunidades"], list)
    assert len(result["alertas"]) == 3
    assert len(result["oportunidades"]) == 3


def test_clean_json_with_markdown_fenced_json():
    raw = """
    ```json
    {
      "pais": "Colombia",
      "resumen_ejecutivo": "Mercado atractivo con cierta incertidumbre operativa.",
      "alertas": ["Seguridad jurídica desigual", "Dependencia sectorial", "Riesgo político moderado"],
      "oportunidades": ["Consumo interno", "Servicios", "Expansión regional"]
    }
    ```
    """

    result = clean_json(raw)

    assert isinstance(result, dict)
    assert result["pais"] == "Colombia"
    assert len(result["alertas"]) == 3
    assert len(result["oportunidades"]) == 3


def test_clean_json_preserves_expected_contract_keys():
    raw = """
    {
      "pais": "Chile",
      "resumen_ejecutivo": "Entorno relativamente estable.",
      "alertas": ["Dependencia externa", "Volatilidad sectorial", "Presión regulatoria puntual"],
      "oportunidades": ["Minería", "Tecnología", "Servicios especializados"]
    }
    """

    result = clean_json(raw)

    expected_keys = {"pais", "resumen_ejecutivo", "alertas", "oportunidades"}
    assert expected_keys == set(result.keys())


def test_clean_json_rejects_incomplete_lists():
    raw = """
    {
      "pais": "Chile",
      "resumen_ejecutivo": "Entorno relativamente estable.",
      "alertas": ["Dependencia externa", "Volatilidad sectorial"],
      "oportunidades": ["Minería", "Tecnología", "Servicios especializados"]
    }
    """

    with pytest.raises(Exception):
        clean_json(raw)


def test_clean_json_raises_on_invalid_json():
    raw = """
    {
      "pais": "México",
      "resumen_ejecutivo": "Texto incompleto",
      "alertas": ["a", "b", "c"],
      "oportunidades": ["x", "y", "z"
    }
    """

    with pytest.raises(Exception):
        clean_json(raw)

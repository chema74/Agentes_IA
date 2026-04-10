from domain.scoring import OFFICIAL_SCORE_KEY, calcular_scores, get_official_score


def build_contexto_rico():
    return {
        "politico": (
            "Se observan riesgos regulatorios, cierta incertidumbre política, "
            "tensión institucional y estabilidad moderada."
        ),
        "economico": (
            "El país presenta crecimiento, inversión, expansión e inflación moderada, "
            "aunque con algo de volatilidad."
        ),
        "regulatorio": (
            "Existen barreras, algunos requisitos de entrada y ciertas restricciones, "
            "aunque también hay acuerdos comerciales parciales."
        ),
        "oportunidades": (
            "Existen oportunidades de exportación en tecnología y servicios."
        ),
    }


def build_contexto_neutro():
    return {
        "politico": "Información general limitada y contexto político mixto.",
        "economico": "Contexto económico sin señales extremas.",
        "regulatorio": "Entorno regulatorio estándar sin fricciones graves.",
        "oportunidades": "Algunas oportunidades moderadas.",
    }


def test_calcular_scores_returns_expected_top_level_keys():
    result = calcular_scores(build_contexto_rico())

    assert isinstance(result, dict)
    assert "scores" in result
    assert "scores_agregados" in result
    assert "pesos_aplicados" in result
    assert "justificacion_scores" in result


def test_calcular_scores_returns_expected_dimension_keys():
    result = calcular_scores(build_contexto_rico())
    scores = result["scores"]

    assert set(scores.keys()) == {
        "riesgo_politico",
        "estabilidad_economica",
        "riesgo_regulatorio",
        "riesgo_geopolitico",
        "riesgo_comercial",
        "riesgo_operativo",
        "ajuste_sectorial",
        "oportunidad_sectorial",
    }


def test_calcular_scores_returns_expected_aggregate_keys():
    result = calcular_scores(build_contexto_rico())
    scores_agregados = result["scores_agregados"]

    assert set(scores_agregados.keys()) == {
        "score_riesgo_pais",
        "score_riesgo_sectorial",
        "score_total",
    }


def test_get_official_score_uses_canonical_aggregate_key():
    result = calcular_scores(build_contexto_rico())

    assert get_official_score(result) == result["scores_agregados"][OFFICIAL_SCORE_KEY]


def test_get_official_score_recomputes_when_aggregates_are_missing():
    result = calcular_scores(build_contexto_rico())
    fallback_result = {"scores": result["scores"]}

    assert get_official_score(fallback_result) == result["scores_agregados"][OFFICIAL_SCORE_KEY]


def test_calcular_scores_score_values_are_numeric_and_reasonable():
    result = calcular_scores(build_contexto_rico())
    scores = result["scores"]

    for value in scores.values():
        assert isinstance(value, (int, float))
        assert 1 <= value <= 10


def test_calcular_scores_aggregate_values_are_numeric_and_reasonable():
    result = calcular_scores(build_contexto_rico())
    scores_agregados = result["scores_agregados"]

    for value in scores_agregados.values():
        assert isinstance(value, (int, float))
        assert 1 <= value <= 10


def test_calcular_scores_returns_weights():
    result = calcular_scores(build_contexto_rico())
    pesos = result["pesos_aplicados"]

    assert isinstance(pesos, dict)
    assert "riesgo_politico" in pesos
    assert "oportunidad_sectorial" in pesos
    assert round(sum(pesos.values()), 2) == 1.00


def test_calcular_scores_returns_justifications_for_each_dimension():
    result = calcular_scores(build_contexto_rico())
    justificaciones = result["justificacion_scores"]

    assert set(justificaciones.keys()) == {
        "riesgo_politico",
        "estabilidad_economica",
        "riesgo_regulatorio",
        "riesgo_geopolitico",
        "riesgo_comercial",
        "riesgo_operativo",
        "ajuste_sectorial",
        "oportunidad_sectorial",
    }

    for key in justificaciones:
        assert isinstance(justificaciones[key], list)
        assert len(justificaciones[key]) >= 1


def test_calcular_scores_handles_neutral_context_without_crashing():
    result = calcular_scores(build_contexto_neutro())

    scores = result["scores"]
    scores_agregados = result["scores_agregados"]
    justificaciones = result["justificacion_scores"]

    assert isinstance(scores, dict)
    assert isinstance(scores_agregados, dict)
    assert isinstance(justificaciones, dict)

    assert set(scores.keys()) == {
        "riesgo_politico",
        "estabilidad_economica",
        "riesgo_regulatorio",
        "riesgo_geopolitico",
        "riesgo_comercial",
        "riesgo_operativo",
        "ajuste_sectorial",
        "oportunidad_sectorial",
    }

    assert set(scores_agregados.keys()) == {
        "score_riesgo_pais",
        "score_riesgo_sectorial",
        "score_total",
    }

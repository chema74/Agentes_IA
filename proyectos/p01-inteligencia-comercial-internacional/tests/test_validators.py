from domain.validators import (
    canonicalize_country_name,
    validate_comparison_inputs,
    parse_and_validate_ranking_countries,
    validate_sector_input,
    validate_tipo_empresa_input,
    sanitize_free_text,
)


# ---------------------------------------------------------------------------
# Tests de alias y canonicalización de países
# ---------------------------------------------------------------------------

def test_canonicalize_country_name_aliases():
    assert canonicalize_country_name("mexico") == "México"
    assert canonicalize_country_name("usa") == "Estados Unidos"
    assert canonicalize_country_name("uk") == "Reino Unido"
    assert canonicalize_country_name("turkey") == "Turquía"


def test_validate_comparison_inputs_ok():
    pais_a, pais_b, errors = validate_comparison_inputs("mexico", "uk")

    assert pais_a == "México"
    assert pais_b == "Reino Unido"
    assert errors == []


def test_validate_comparison_inputs_duplicate_logical_country():
    pais_a, pais_b, errors = validate_comparison_inputs("mexico", "México")

    assert pais_a == "México"
    assert pais_b == "México"
    assert "Debes introducir dos países diferentes." in errors


def test_parse_and_validate_ranking_countries_ok():
    countries, errors = parse_and_validate_ranking_countries(
        "mexico, usa, uk, morocco",
        min_countries=2,
        max_countries=8,
    )

    assert countries == ["México", "Estados Unidos", "Reino Unido", "Marruecos"]
    assert errors == []


def test_parse_and_validate_ranking_countries_duplicates():
    countries, errors = parse_and_validate_ranking_countries(
        "mexico, México, usa",
        min_countries=2,
        max_countries=8,
    )

    assert countries == ["México", "Estados Unidos"]
    assert any("duplicados" in err.lower() for err in errors)


def test_parse_and_validate_ranking_countries_too_many():
    countries, errors = parse_and_validate_ranking_countries(
        "mexico, usa, uk, morocco, turkey, france, germany, italy, spain",
        min_countries=2,
        max_countries=8,
    )

    assert len(countries) == 9
    assert any("máximo de 8" in err.lower() for err in errors)


def test_parse_and_validate_ranking_countries_empty():
    countries, errors = parse_and_validate_ranking_countries(
        "",
        min_countries=2,
        max_countries=8,
    )

    assert countries == []
    assert errors


# ---------------------------------------------------------------------------
# Tests de nuevos alias (~50 países)
# ---------------------------------------------------------------------------

def test_canonicalize_new_aliases_english():
    assert canonicalize_country_name("germany") == "Alemania"
    assert canonicalize_country_name("france") == "Francia"
    assert canonicalize_country_name("italy") == "Italia"
    assert canonicalize_country_name("brazil") == "Brasil"
    assert canonicalize_country_name("japan") == "Japón"
    assert canonicalize_country_name("south korea") == "Corea del Sur"
    assert canonicalize_country_name("netherlands") == "Países Bajos"
    assert canonicalize_country_name("sweden") == "Suecia"
    assert canonicalize_country_name("norway") == "Noruega"
    assert canonicalize_country_name("denmark") == "Dinamarca"


def test_canonicalize_new_aliases_spanish():
    assert canonicalize_country_name("holanda") == "Países Bajos"
    assert canonicalize_country_name("suiza") == "Suiza"
    assert canonicalize_country_name("grecia") == "Grecia"
    assert canonicalize_country_name("rumania") == "Rumanía"
    assert canonicalize_country_name("tailandia") == "Tailandia"
    assert canonicalize_country_name("singapur") == "Singapur"
    assert canonicalize_country_name("filipinas") == "Filipinas"
    assert canonicalize_country_name("ucrania") == "Ucrania"
    assert canonicalize_country_name("sudafrica") == "Sudáfrica"
    assert canonicalize_country_name("arabia saudi") == "Arabia Saudí"


def test_canonicalize_latam_aliases():
    assert canonicalize_country_name("venezuela") == "Venezuela"
    assert canonicalize_country_name("ecuador") == "Ecuador"
    assert canonicalize_country_name("bolivia") == "Bolivia"
    assert canonicalize_country_name("costa rica") == "Costa Rica"
    assert canonicalize_country_name("panama") == "Panamá"


# ---------------------------------------------------------------------------
# Tests de fuzzy matching con rapidfuzz (erratas comunes)
# ---------------------------------------------------------------------------

def test_fuzzy_match_typo_alemania():
    # "Alemana" → "Alemania"
    result = canonicalize_country_name("Alemana")
    assert result == "Alemania"


def test_fuzzy_match_typo_australia():
    # "Australa" → "Australia"
    result = canonicalize_country_name("Australa")
    assert result == "Australia"


def test_fuzzy_match_typo_indonesia():
    # "Indonsia" → "Indonesia"
    result = canonicalize_country_name("Indonsia")
    assert result == "Indonesia"


def test_fuzzy_match_english_typo_sweden():
    # "Swden" → "Suecia" (via "sweden")
    result = canonicalize_country_name("Swden")
    assert result == "Suecia"


def test_fuzzy_no_false_positive():
    # Texto sin similitud suficiente → fallback capitalize
    result = canonicalize_country_name("Xyz")
    assert result == "Xyz"


# ---------------------------------------------------------------------------
# Tests de Fase 17: sectores y tipos de empresa
# ---------------------------------------------------------------------------

def test_validate_sector_input_ok():
    canon, errors = validate_sector_input("Tecnología")
    assert canon == "Tecnología"
    assert errors == []


def test_validate_sector_input_case_insensitive():
    canon, errors = validate_sector_input("tecnologia")
    assert canon == "Tecnología"
    assert errors == []


def test_validate_sector_input_invalid():
    canon, errors = validate_sector_input("Moda")
    assert canon == ""
    assert len(errors) == 1
    assert "no reconocido" in errors[0]


def test_validate_tipo_empresa_input_ok():
    canon, errors = validate_tipo_empresa_input("PYME")
    assert canon == "PYME"
    assert errors == []


def test_validate_tipo_empresa_input_invalid():
    canon, errors = validate_tipo_empresa_input("Multinacional")
    assert canon == ""
    assert len(errors) == 1
    assert "no reconocido" in errors[0]


def test_sanitize_free_text_ok():
    text = "Buscamos expandirnos al mercado asiático en el sector tecnológico."
    cleaned, errors = sanitize_free_text(text, "Contexto")
    assert errors == []
    assert cleaned == text.strip()


def test_sanitize_free_text_too_long():
    text = "a" * 501
    cleaned, errors = sanitize_free_text(text, "Contexto")
    assert cleaned == ""
    assert any("máximo" in e for e in errors)

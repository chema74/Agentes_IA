from app import streamlit_app
from domain.demo_data import get_demo_supported_countries, split_demo_supported_countries


def test_get_demo_supported_countries_matches_catalog():
    countries = get_demo_supported_countries()

    assert isinstance(countries, list)
    assert "México" in countries
    assert "Alemania" in countries


def test_split_demo_supported_countries_separates_supported_and_unsupported():
    soportados, no_soportados = split_demo_supported_countries(
        ["mexico", "Francia", "Alemania", "Argentina"]
    )

    assert soportados == ["México", "Alemania"]
    assert no_soportados == ["Francia", "Argentina"]


def test_parse_ranking_countries_input_accepts_line_breaks():
    countries, errors = streamlit_app._parse_ranking_countries_input(
        "mexico\nalemania\nmorocco"
    )

    assert countries == ["México", "Alemania", "Marruecos"]
    assert errors == []


def test_build_demo_unavailable_message_is_explicit():
    message = streamlit_app._build_demo_unavailable_message(["Francia", "Argentina"])

    assert "modo demo" in message
    assert "Francia, Argentina" in message
    assert "modo producción" in message


def test_build_demo_internal_error_message_is_not_generic():
    message = streamlit_app._build_demo_internal_error_message(["México"])

    assert "error interno" in message
    assert "fixtures demo" in message
    assert "México" in message

"""
domain/validators.py
Sincronizado con tests/test_validators.py - Fase 18C + Fase 17 (rapidfuzz)
"""
from __future__ import annotations

import re
import unicodedata
from typing import Dict, List

from domain.i18n import get_text

try:
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz
    _RAPIDFUZZ_AVAILABLE = True
except ImportError:  # pragma: no cover
    _RAPIDFUZZ_AVAILABLE = False

# Umbral mínimo de similitud para el matching difuso (0-100)
_FUZZY_THRESHOLD = 85


COUNTRY_ALIASES: Dict[str, str] = {
    # México
    "mexico": "México",
    "méxico": "México",
    # Marruecos
    "marruecos": "Marruecos",
    "morocco": "Marruecos",
    # Vietnam
    "vietnam": "Vietnam",
    "viet nam": "Vietnam",
    # Colombia
    "colombia": "Colombia",
    # Turquía
    "turquia": "Turquía",
    "turquía": "Turquía",
    "turkey": "Turquía",
    # España
    "espana": "España",
    "españa": "España",
    "spain": "España",
    # Francia
    "francia": "Francia",
    "france": "Francia",
    # Alemania
    "alemania": "Alemania",
    "germany": "Alemania",
    # Italia
    "italia": "Italia",
    "italy": "Italia",
    # Portugal
    "portugal": "Portugal",
    # Reino Unido
    "reinounido": "Reino Unido",
    "reino unido": "Reino Unido",
    "uk": "Reino Unido",
    "united kingdom": "Reino Unido",
    "gran bretana": "Reino Unido",
    "gran bretaña": "Reino Unido",
    "inglaterra": "Reino Unido",
    # Estados Unidos
    "estados unidos": "Estados Unidos",
    "eeuu": "Estados Unidos",
    "e.e.u.u.": "Estados Unidos",
    "usa": "Estados Unidos",
    "u.s.a.": "Estados Unidos",
    "united states": "Estados Unidos",
    # Canadá
    "canada": "Canadá",
    "canadá": "Canadá",
    # Chile
    "chile": "Chile",
    # Perú
    "peru": "Perú",
    "perú": "Perú",
    # Argentina
    "argentina": "Argentina",
    # Brasil
    "brasil": "Brasil",
    "brazil": "Brasil",
    # China
    "china": "China",
    # India
    "india": "India",
    # Japón
    "japon": "Japón",
    "japón": "Japón",
    "japan": "Japón",
    # Corea del Sur
    "corea del sur": "Corea del Sur",
    "south korea": "Corea del Sur",
    "korea": "Corea del Sur",
    # Emiratos Árabes Unidos
    "emiratos arabes unidos": "Emiratos Árabes Unidos",
    "emiratos árabes unidos": "Emiratos Árabes Unidos",
    "uae": "Emiratos Árabes Unidos",
    "ea u": "Emiratos Árabes Unidos",
    # Arabia Saudí
    "arabia saudi": "Arabia Saudí",
    "arabia saudí": "Arabia Saudí",
    "saudi arabia": "Arabia Saudí",
    "ksa": "Arabia Saudí",
    # Australia
    "australia": "Australia",
    # Nueva Zelanda
    "nueva zelanda": "Nueva Zelanda",
    "new zealand": "Nueva Zelanda",
    # Sudáfrica
    "sudafrica": "Sudáfrica",
    "sudáfrica": "Sudáfrica",
    "south africa": "Sudáfrica",
    # Nigeria
    "nigeria": "Nigeria",
    # Egipto
    "egipto": "Egipto",
    "egypt": "Egipto",
    # Israel
    "israel": "Israel",
    # Indonesia
    "indonesia": "Indonesia",
    # Malasia
    "malasia": "Malasia",
    "malaysia": "Malasia",
    # Tailandia
    "tailandia": "Tailandia",
    "thailand": "Tailandia",
    # Filipinas
    "filipinas": "Filipinas",
    "philippines": "Filipinas",
    # Singapur
    "singapur": "Singapur",
    "singapore": "Singapur",
    # Taiwán
    "taiwan": "Taiwán",
    "taiwán": "Taiwán",
    # Rusia
    "rusia": "Rusia",
    "russia": "Rusia",
    # Polonia
    "polonia": "Polonia",
    "poland": "Polonia",
    # Países Bajos
    "paises bajos": "Países Bajos",
    "países bajos": "Países Bajos",
    "holanda": "Países Bajos",
    "netherlands": "Países Bajos",
    "holland": "Países Bajos",
    # Bélgica
    "belgica": "Bélgica",
    "bélgica": "Bélgica",
    "belgium": "Bélgica",
    # Suiza
    "suiza": "Suiza",
    "switzerland": "Suiza",
    # Austria
    "austria": "Austria",
    # Suecia
    "suecia": "Suecia",
    "sweden": "Suecia",
    # Noruega
    "noruega": "Noruega",
    "norway": "Noruega",
    # Dinamarca
    "dinamarca": "Dinamarca",
    "denmark": "Dinamarca",
    # Finlandia
    "finlandia": "Finlandia",
    "finland": "Finlandia",
    # Grecia
    "grecia": "Grecia",
    "greece": "Grecia",
    # República Checa
    "republica checa": "República Checa",
    "república checa": "República Checa",
    "czech republic": "República Checa",
    "czechia": "República Checa",
    # Hungría
    "hungria": "Hungría",
    "hungría": "Hungría",
    "hungary": "Hungría",
    # Rumanía
    "rumania": "Rumanía",
    "rumanía": "Rumanía",
    "romania": "Rumanía",
    # Ucrania
    "ucrania": "Ucrania",
    "ukraine": "Ucrania",
    # Venezuela
    "venezuela": "Venezuela",
    # Ecuador
    "ecuador": "Ecuador",
    # Bolivia
    "bolivia": "Bolivia",
    # Uruguay
    "uruguay": "Uruguay",
    # Paraguay
    "paraguay": "Paraguay",
    # Cuba
    "cuba": "Cuba",
    # Panamá
    "panama": "Panamá",
    "panamá": "Panamá",
    # Costa Rica
    "costa rica": "Costa Rica",
    # Pakistán
    "pakistan": "Pakistán",
    "pakistán": "Pakistán",
}


def _strip_accents(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch))


def normalize_text_for_matching(text: str) -> str:
    text = text.strip().lower()
    text = _strip_accents(text)
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text)).strip()


def _fuzzy_match_country(normalized: str) -> str | None:
    """Busca la clave más cercana en COUNTRY_ALIASES con rapidfuzz."""
    if not _RAPIDFUZZ_AVAILABLE:
        return None
    result = rf_process.extractOne(
        normalized,
        list(COUNTRY_ALIASES.keys()),
        scorer=rf_fuzz.WRatio,
        score_cutoff=_FUZZY_THRESHOLD,
    )
    if result is not None:
        best_key, _score, _idx = result
        return COUNTRY_ALIASES[best_key]
    return None


def canonicalize_country_name(country: str) -> str:
    raw = country.strip()
    if not raw:
        return ""
    normalized = normalize_text_for_matching(raw)
    compact = normalized.replace(" ", "")

    if normalized in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[normalized]
    if compact in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[compact]

    fuzzy_result = _fuzzy_match_country(normalized)
    if fuzzy_result is not None:
        return fuzzy_result

    return " ".join(word.capitalize() for word in raw.split())


def validate_country_input(country: str, field_name: str) -> tuple[str, List[str]]:
    if not country or not country.strip():
        return "", [f"{field_name}: el país no puede estar vacío."]
    cleaned = canonicalize_country_name(country)
    if len(cleaned) < 2:
        return "", [f"{field_name}: el país introducido no parece válido."]
    return cleaned, []


def validate_comparison_inputs(pais_a: str, pais_b: str) -> tuple[str, str, List[str]]:
    p_a, err_a = validate_country_input(pais_a, "País A")
    p_b, err_b = validate_country_input(pais_b, "País B")
    errors = err_a + err_b
    if not errors and normalize_text_for_matching(p_a) == normalize_text_for_matching(p_b):
        errors.append("Debes introducir dos países diferentes.")
    return p_a, p_b, errors


def parse_and_validate_ranking_countries(raw_text: str, min_countries: int = 2, max_countries: int = 8) -> tuple[List[str], List[str]]:
    if not raw_text or not raw_text.strip():
        return [], ["Debes introducir al menos dos países."]
    parts = [p.strip() for p in raw_text.split(",") if p.strip()]
    errors = []
    if len(parts) < min_countries:
        errors.append(f"Introduce al menos {min_countries} países para generar ranking.")
    if len(parts) > max_countries:
        errors.append(f"Por ahora el ranking admite un máximo de {max_countries} países por ejecución.")

    res, seen, dups = [], set(), []
    for p in parts:
        c, err = validate_country_input(p, "Ranking")
        if err:
            errors.extend(err)
            continue
        key = normalize_text_for_matching(c)
        if key in seen:
            dups.append(c)
            continue
        seen.add(key)
        res.append(c)

    if dups:
        errors.append(f"Hay países duplicados en el ranking: {', '.join(sorted(set(dups)))}.")
    return res, errors


# --- FASE 18C: VALIDACIÓN i18n ---

def validate_sector_input(sector: str, lang: str = "es") -> tuple[str, List[str]]:
    permitidos = get_text("sectors", section="domain", lang=lang)
    norm_in = normalize_text_for_matching(sector)
    for p in permitidos:
        if normalize_text_for_matching(p) == norm_in:
            return p, []
    opciones = ", ".join(permitidos)
    return "", [f"Sector '{sector}' no reconocido. Opciones válidas: {opciones}."]


def validate_tipo_empresa_input(tipo: str, lang: str = "es") -> tuple[str, List[str]]:
    permitidos = get_text("company_types", section="domain", lang=lang)
    norm_in = normalize_text_for_matching(tipo)
    for p in permitidos:
        if normalize_text_for_matching(p) == norm_in:
            return p, []
    opciones = ", ".join(permitidos)
    return "", [f"Tipo de empresa '{tipo}' no reconocido. Opciones válidas: {opciones}."]


def sanitize_free_text(text: str, field_name: str = "Campo") -> tuple[str, List[str]]:
    if not text.strip():
        return "", [f"{field_name}: el texto no puede estar vacío."]
    cleaned = re.sub(r"\s+", " ", text.strip())
    if len(cleaned) > 500:
        return "", [f"{field_name}: el texto supera el máximo de 500 caracteres ({len(cleaned)} introducidos)."]
    return cleaned, []

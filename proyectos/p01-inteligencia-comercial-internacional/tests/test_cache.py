from pathlib import Path

from domain import cache


def test_build_cache_key_is_stable():
    key1 = cache.build_cache_key("México", "Tecnología", "PYME exportadora")
    key2 = cache.build_cache_key("mexico", "Tecnología", "PYME exportadora")

    assert isinstance(key1, str)
    assert key1 == key2


def test_save_and_load_country_analysis_cache(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache_test"
    monkeypatch.setattr(cache, "CACHE_BASE_DIR", cache_dir)

    payload = {
        "pais": "México",
        "resumen_ejecutivo": "Texto de prueba",
        "scores": {
            "riesgo_politico": 4,
            "riesgo_comercial": 5,
            "estabilidad_economica": 7,
        },
    }

    saved_path = cache.save_country_analysis_to_cache(
        pais="México",
        sector="Tecnología",
        tipo_empresa="PYME exportadora",
        data=payload,
    )

    assert saved_path.exists()
    assert saved_path.suffix == ".json"

    loaded = cache.load_country_analysis_from_cache(
        pais="México",
        sector="Tecnología",
        tipo_empresa="PYME exportadora",
    )

    assert loaded is not None
    assert loaded["metadata"]["pais"] == "México"
    assert loaded["result"]["resumen_ejecutivo"] == "Texto de prueba"
    assert loaded["result"]["scores"]["riesgo_politico"] == 4


def test_load_country_analysis_cache_miss(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache_test"
    monkeypatch.setattr(cache, "CACHE_BASE_DIR", cache_dir)

    loaded = cache.load_country_analysis_from_cache(
        pais="Chile",
        sector="Tecnología",
        tipo_empresa="PYME exportadora",
    )

    assert loaded is None


def test_clear_country_analysis_cache(tmp_path, monkeypatch):
    cache_dir = tmp_path / "cache_test"
    monkeypatch.setattr(cache, "CACHE_BASE_DIR", cache_dir)

    for idx in range(3):
        cache.save_country_analysis_to_cache(
            pais=f"Pais {idx}",
            sector="General",
            tipo_empresa="Consultora",
            data={"ok": True, "idx": idx},
        )

    stats_before = cache.get_cache_stats()
    assert stats_before["total_files"] == 3

    deleted = cache.clear_country_analysis_cache()
    assert deleted == 3

    stats_after = cache.get_cache_stats()
    assert stats_after["total_files"] == 0
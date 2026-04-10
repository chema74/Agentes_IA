import os
import pytest


@pytest.fixture(autouse=True)
def set_dummy_env_vars(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "dummy-groq-key")
    monkeypatch.setenv("TAVILY_API_KEY", "dummy-tavily-key")

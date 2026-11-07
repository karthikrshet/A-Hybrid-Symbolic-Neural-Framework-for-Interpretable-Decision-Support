import os
from pathlib import Path

from app.config import _load_env_file
from app.core.llm import resolve_config


def test_env_file_is_loaded_without_overriding_real_variables(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    env = tmp_path / ".env"
    env.write_text("# comment\nNS_TEST_A=from_file\nNS_TEST_B='quoted value'\nNS_TEST_EMPTY=\nNS_TEST_REAL=from_file\n", encoding="utf-8")
    monkeypatch.setenv("NS_TEST_REAL", "from_shell")
    monkeypatch.delenv("NS_TEST_A", raising=False)
    monkeypatch.delenv("NS_TEST_B", raising=False)
    _load_env_file(env)
    assert os.environ["NS_TEST_A"] == "from_file"
    assert os.environ["NS_TEST_B"] == "quoted value"
    assert "NS_TEST_EMPTY" not in os.environ  # empty values are skipped
    assert os.environ["NS_TEST_REAL"] == "from_shell"  # the real environment wins


def test_llm_provider_from_environment(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-test")
    cfg = resolve_config({})
    assert cfg is not None and cfg.provider == "gemini" and cfg.model == "gemini-2.5-flash" and cfg.source == "environment"
    monkeypatch.setenv("LLM_PROVIDER", "off")
    assert resolve_config({}) is None
    # the chat settings dialog (request headers) still takes precedence
    assert resolve_config({"X-LLM-Provider": "openai", "X-LLM-Key": "sk-x"}).provider == "openai"  # type: ignore[union-attr]

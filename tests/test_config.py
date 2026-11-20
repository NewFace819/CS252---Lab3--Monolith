from pathlib import Path

import pytest

from assistant_core.config import load_settings
from assistant_core.errors import ConfigError

VARIABLES = (
    "ASSISTANT_DATA_DIR",
    "LLM_PROVIDER",
    "LLM_API_KEY",
    "CREDIT_RATE_VND",
    "RETAKE_MULTIPLIER",
    "MAX_CREDITS",
    "LOG_LEVEL",
)

LAB6_VARIABLES = (
    "KB_DIR",
    "RETRIEVAL_KIND",
    "RETRIEVAL_MIN_SCORE",
    "LLM_MODEL",
    "LLM_BASE_URL",
    "LLM_TIMEOUT_S",
    "PROMPT_VERSION",
)


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for name in (*VARIABLES, *LAB6_VARIABLES):
        # Register absent variables too, so dotenv additions are undone by pytest.
        monkeypatch.setenv(name, "")
        monkeypatch.delenv(name, raising=False)


def test_defaults_without_env_file():
    settings = load_settings(None)
    assert settings.data_dir == Path("data")
    assert settings.llm_provider == "stub"
    assert settings.llm_api_key is None
    assert settings.credit_rate_vnd == 450_000
    assert settings.retake_multiplier == 1.5
    assert settings.max_credits == 30
    assert settings.log_level == "INFO"


def test_all_environment_fields(monkeypatch, tmp_path):
    values = [str(tmp_path), "provider", "test-only-key", "500000", "2.0", "24", "debug"]
    for name, value in zip(VARIABLES, values, strict=True):
        monkeypatch.setenv(name, value)
    settings = load_settings(None)
    assert settings.data_dir == tmp_path
    assert settings.llm_provider == "provider"
    assert settings.llm_api_key == "test-only-key"
    assert settings.credit_rate_vnd == 500_000
    assert settings.retake_multiplier == 2.0
    assert settings.max_credits == 24
    assert settings.log_level == "DEBUG"


def test_lab6_defaults_without_env_file():
    settings = load_settings(None)
    assert settings.kb_dir == Path("data/kb")
    assert settings.retrieval_kind == "bm25"
    assert settings.retrieval_min_score == 2.0
    assert settings.llm_model == "llama3.2"
    assert settings.llm_base_url is None
    assert settings.llm_timeout_s == 5.0
    assert settings.prompt_version == "answer_v1"


def test_lab6_loads_environment_and_dotenv(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "KB_DIR=fixtures/kb\nRETRIEVAL_KIND=hybrid\nRETRIEVAL_MIN_SCORE=1.25\n"
        "LLM_MODEL=dotenv-model\nLLM_BASE_URL=http://localhost:11434\n"
        "LLM_TIMEOUT_S=7.5\nPROMPT_VERSION=answer_v2\nLLM_PROVIDER=ollama\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LLM_MODEL", " process-model ")
    settings = load_settings(str(env_file))
    assert settings.kb_dir == Path("fixtures/kb")
    assert settings.retrieval_kind == "hybrid"
    assert settings.retrieval_min_score == 1.25
    assert settings.llm_model == "process-model"
    assert settings.llm_base_url == "http://localhost:11434"
    assert settings.llm_timeout_s == 7.5
    assert settings.prompt_version == "answer_v2"
    assert settings.llm_provider == "ollama"
    assert settings.llm_api_key is None


@pytest.mark.parametrize("name", ["RETRIEVAL_MIN_SCORE", "LLM_TIMEOUT_S"])
def test_lab6_invalid_numbers_raise_config_error(monkeypatch, name):
    monkeypatch.setenv(name, "not-a-number")
    with pytest.raises(ConfigError, match="numeric environment variables"):
        load_settings(None)


def test_dotenv_loads_but_does_not_override_process(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("CREDIT_RATE_VND=600000\nMAX_CREDITS=25\n", encoding="utf-8")
    monkeypatch.setenv("CREDIT_RATE_VND", "700000")
    settings = load_settings(str(env_file))
    assert settings.credit_rate_vnd == 700_000
    assert settings.max_credits == 25


@pytest.mark.parametrize("key", [None, "", "   "])
def test_openai_requires_nonempty_key(monkeypatch, key):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    if key is not None:
        monkeypatch.setenv("LLM_API_KEY", key)
    with pytest.raises(ConfigError, match="LLM_API_KEY"):
        load_settings(None)


def test_key_not_in_repr_or_print(monkeypatch, capsys):
    key = "test-only-secret-value"
    monkeypatch.setenv("LLM_API_KEY", key)
    settings = load_settings(None)
    assert settings.llm_api_key == key
    assert key not in repr(settings)
    print(settings)
    assert key not in capsys.readouterr().out


@pytest.mark.parametrize(
    "name, value",
    [
        ("CREDIT_RATE_VND", "abc"),
        ("MAX_CREDITS", "1.5"),
        ("RETAKE_MULTIPLIER", "bad"),
        ("CREDIT_RATE_VND", "0"),
        ("MAX_CREDITS", "-1"),
        ("RETAKE_MULTIPLIER", "0"),
        ("RETAKE_MULTIPLIER", "nan"),
        ("RETAKE_MULTIPLIER", "inf"),
        ("LOG_LEVEL", "verbose"),
        ("LLM_PROVIDER", " "),
    ],
)
def test_invalid_settings_have_named_errors(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError):
        load_settings(None)


def test_error_does_not_echo_environment_secret(monkeypatch):
    secret = "test-secret-in-invalid-setting"
    monkeypatch.setenv("LLM_API_KEY", secret)
    monkeypatch.setenv("MAX_CREDITS", secret)
    with pytest.raises(ConfigError) as caught:
        load_settings(None)
    assert secret not in str(caught.value)
    assert caught.value.__suppress_context__


def test_example_documents_all_variables():
    example = Path(__file__).resolve().parents[1] / ".env.example"
    entries = dict(line.split("=", 1) for line in example.read_text().splitlines() if line and not line.startswith("#"))
    assert set(entries) == set(VARIABLES)
    assert entries["LLM_API_KEY"] == ""

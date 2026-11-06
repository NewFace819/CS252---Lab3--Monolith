"""Lab 4 config checks without changing the original Week 3 tests."""

import pytest

from assistant_core.config import load_settings
from assistant_core.errors import ConfigError

API_VARIABLES = (
    "API_ADMIN_KEY",
    "WEATHER_URL",
    "WEATHER_TIMEOUT_S",
    "CAMPUS_LAT",
    "CAMPUS_LON",
    "RATE_LIMIT_PER_MIN",
)


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for name in (
        "ASSISTANT_DATA_DIR",
        "LLM_PROVIDER",
        "LLM_API_KEY",
        "CREDIT_RATE_VND",
        "RETAKE_MULTIPLIER",
        "MAX_CREDITS",
        "LOG_LEVEL",
        *API_VARIABLES,
    ):
        # Register absent names too, so values added by dotenv are restored.
        monkeypatch.setenv(name, "")
        monkeypatch.delenv(name)


def test_api_defaults_disable_admin_until_key_is_configured():
    settings = load_settings(None)
    assert settings.api_admin_key is None
    assert settings.weather_url == "https://api.open-meteo.com/v1/forecast"
    assert settings.weather_timeout_s == 3.0
    assert settings.campus_lat == 10.7626
    assert settings.campus_lon == 106.6822
    assert settings.rate_limit_per_min == 30


def test_api_environment_fields(monkeypatch):
    values = ("test-admin", "https://example.test/weather", "2.5", "11.1", "107.2", "5")
    for name, value in zip(API_VARIABLES, values, strict=True):
        monkeypatch.setenv(name, value)
    settings = load_settings(None)
    assert settings.api_admin_key == "test-admin"
    assert settings.weather_url == "https://example.test/weather"
    assert settings.weather_timeout_s == 2.5
    assert settings.campus_lat == 11.1
    assert settings.campus_lon == 107.2
    assert settings.rate_limit_per_min == 5


def test_admin_key_from_dotenv_and_process_precedence(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("API_ADMIN_KEY=test-dotenv-admin\n", encoding="utf-8")
    assert load_settings(str(env_file)).api_admin_key == "test-dotenv-admin"
    monkeypatch.setenv("API_ADMIN_KEY", "test-process-admin")
    assert load_settings(str(env_file)).api_admin_key == "test-process-admin"


def test_admin_key_is_trimmed_and_not_printed(monkeypatch, capsys):
    key = "test-only-admin-secret"
    monkeypatch.setenv("API_ADMIN_KEY", f"  {key}  ")
    settings = load_settings(None)
    assert settings.api_admin_key == key
    assert key not in repr(settings)
    print(settings)
    assert key not in capsys.readouterr().out


@pytest.mark.parametrize("key", ["", "   "])
def test_blank_admin_key_stays_disabled(monkeypatch, key):
    monkeypatch.setenv("API_ADMIN_KEY", key)
    assert load_settings(None).api_admin_key is None


@pytest.mark.parametrize("name", ["WEATHER_TIMEOUT_S", "CAMPUS_LAT", "CAMPUS_LON", "RATE_LIMIT_PER_MIN"])
def test_invalid_api_numeric_value_does_not_echo_secrets(monkeypatch, name):
    secret = "test-only-invalid-secret"
    monkeypatch.setenv("API_ADMIN_KEY", secret)
    monkeypatch.setenv(name, secret)
    with pytest.raises(ConfigError) as caught:
        load_settings(None)
    assert secret not in str(caught.value)

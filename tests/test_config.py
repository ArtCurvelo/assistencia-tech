import pytest

from assistencia_tech.config import DEFAULT_TIMEOUT_SECONDS, load_settings
from assistencia_tech.data.errors import ConfigurationError


def test_defaults_to_demo_without_configuration():
    settings = load_settings({})
    assert settings.data_source == "demo"
    assert settings.xano_base_url is None
    assert settings.xano_timeout_seconds == DEFAULT_TIMEOUT_SECONDS


def test_blank_values_are_treated_as_missing():
    settings = load_settings({"ASSISTENCIA_DATA_SOURCE": "  ", "XANO_BASE_URL": " "})
    assert settings.data_source == "demo"
    assert settings.xano_base_url is None


def test_reads_xano_settings_case_insensitive_and_strips_trailing_slash():
    settings = load_settings(
        {
            "ASSISTENCIA_DATA_SOURCE": "XANO",
            "XANO_BASE_URL": "https://exemplo.invalid/api/",
            "XANO_TIMEOUT_SECONDS": "2.5",
        }
    )
    assert settings.data_source == "xano"
    assert settings.xano_base_url == "https://exemplo.invalid/api"
    assert settings.xano_timeout_seconds == 2.5


def test_unknown_source_names_value_and_accepted_options():
    with pytest.raises(ConfigurationError) as info:
        load_settings({"ASSISTENCIA_DATA_SOURCE": "sqlite"})
    message = info.value.user_message
    assert "sqlite" in message
    assert "demo" in message and "xano" in message


@pytest.mark.parametrize("raw", ["abc", "0", "-3"])
def test_invalid_timeout_is_rejected(raw):
    with pytest.raises(ConfigurationError):
        load_settings({"XANO_TIMEOUT_SECONDS": raw})

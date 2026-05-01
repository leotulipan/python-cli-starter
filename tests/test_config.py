from python_cli import config as config_module
from python_cli.config import Settings


def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.setattr(config_module, "_env_files", ())
    monkeypatch.setattr(config_module, "_settings", None)
    settings = Settings(_env_file=None)
    assert settings.app_env == "dev"
    assert settings.log_level == "INFO"

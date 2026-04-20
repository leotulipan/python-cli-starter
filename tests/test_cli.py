from typer.testing import CliRunner

from python_cli.cli import app


def test_version(runner: CliRunner) -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "python-cli" in result.stdout


def test_version_short_flag(runner: CliRunner) -> None:
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert "python-cli" in result.stdout


def test_greet(runner: CliRunner) -> None:
    result = runner.invoke(app, ["greet", "Ada"])
    assert result.exit_code == 0
    assert "Ada" in result.stdout

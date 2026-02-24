from typer.testing import CliRunner

from python_cli.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "python-cli" in result.stdout


def test_greet() -> None:
    result = runner.invoke(app, ["greet", "Ada"])
    assert result.exit_code == 0
    assert "Ada" in result.stdout

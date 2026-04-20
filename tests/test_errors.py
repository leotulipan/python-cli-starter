from typer.testing import CliRunner

from python_cli.cli import app


def test_fail_exits_nonzero(runner: CliRunner) -> None:
    result = runner.invoke(app, ["fail"])
    assert result.exit_code != 0
    assert result.exit_code == 2

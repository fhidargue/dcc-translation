import subprocess
import pytest

pytestmark = pytest.mark.local


PROFILE_TARGET = "unreal"


def run_cli(args):
    """
    Helper to run CLI command via uv.
    """

    return subprocess.run(
        ["uv", "run", "dcc-translate", *args],
        capture_output=True,
        text=True,
    )


def test_cli_publish(tmp_path):
    usd_path = tmp_path / "scene.usda"
    db_path = tmp_path / "translations.db"

    result = run_cli(
        [
            "publish",
            "--dcc",
            "mock",
            "--target",
            PROFILE_TARGET,
            "--out",
            str(usd_path),
            "--db",
            str(db_path),
        ]
    )

    assert result.returncode == 0
    assert usd_path.exists()
    assert db_path.exists()

    metadata_file = usd_path.with_suffix(".metadata.json")
    assert metadata_file.exists()


def test_cli_validate():
    result = run_cli(
        [
            "validate",
            "--dcc",
            "mock",
            "--target",
            PROFILE_TARGET,
        ]
    )

    assert result.returncode == 0
    assert "Validation completed" in result.stdout


def test_cli_inspect(tmp_path):
    usd_path = tmp_path / "scene.usda"
    db_path = tmp_path / "translations.db"

    run_cli(
        [
            "publish",
            "--dcc",
            "mock",
            "--target",
            PROFILE_TARGET,
            "--out",
            str(usd_path),
            "--db",
            str(db_path),
        ]
    )

    result = run_cli(
        [
            "inspect",
            "--db",
            str(db_path),
        ]
    )

    assert result.returncode == 0
    assert "Publish history" in result.stdout

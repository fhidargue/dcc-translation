import nox
import os
from pathlib import Path


MAYAPY = os.environ.get(
    "MAYAPY_EXECUTABLE",
    "/Applications/Autodesk/maya2025/Maya.app/Contents/bin/mayapy",
)


def _ensure_mayapy(session):
    if not Path(MAYAPY).exists():
        session.skip(f"mayapy command not found at path: {MAYAPY}")


@nox.session
def local(session):
    """Run normal uv based tests"""
    session.run("uv", "run", "pytest", "-m", "local")


@nox.session
def maya(session):
    """Run Maya standalone tests"""
    _ensure_mayapy(session)

    session.run(
        MAYAPY,
        "-m",
        "pytest",
        "dcc_translation/tests/maya",
        "-m",
        "maya",
        external=True,
    )


@nox.session
def all(session):
    """Run all tests"""
    session.run("uv", "run", "pytest", "-m", "local")

    _ensure_mayapy(session)

    session.run(
        MAYAPY,
        "-m",
        "pytest",
        "dcc_translation/tests/maya",
        "-m",
        "maya",
        external=True,
    )

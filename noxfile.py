import os
import nox
import platform
from pathlib import Path

system = platform.system()

# Default mayapy paths by OS
# TODO: Implement Windows mayapy location
if system == "Darwin":
    default_mayapy = "/Applications/Autodesk/maya2025/Maya.app/Contents/bin/mayapy"
elif system == "Linux":
    default_mayapy = "/opt/autodesk/maya2025/bin/mayapy"
else:
    default_mayapy = None

MAYAPY = os.environ.get(
    "MAYAPY_EXECUTABLE",
    default_mayapy,
)


def _ensure_mayapy(session):
    """
    Ensure mayapy exists before running Maya tests
    """
    if not MAYAPY:
        session.skip(f"Unsupported operating system: {system}")

    if not Path(MAYAPY).exists():
        session.skip(f"mayapy command not found at path: {MAYAPY}")


@nox.session
def local(session):
    """Run normal uv based tests"""
    session.run("uv", "run", "pytest", "dcc_translation/tests/local", "-m", "local")


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
    session.run("uv", "run", "pytest", "dcc_translation/tests/local", "-m", "local")

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

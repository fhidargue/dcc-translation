#!/usr/bin/env -S uv run --script

import platform
import sys
import os
from pathlib import Path


MODULE_NAME = "dcc_translation"
MODULE_VERSION = "1.0.0"


def get_maya_root() -> Path:
    """
    Return Maya preferences root folder depending on OS
    """

    home = Path.home()
    system = platform.system()

    if system == "Darwin":
        return home / "Library/Preferences/Autodesk/maya"
    if system == "Linux":
        return home / "maya"
    if system == "Windows":
        return home / "Documents/maya"

    raise RuntimeError(f"Unsupported OS: {system}")


def get_maya_version(root: Path) -> Path:
    """
    Detects installed Maya version
    """

    if not root.exists():
        raise FileNotFoundError(f"Maya root directory not found: {root}")

    versions = sorted(
        [
            directory
            for directory in root.iterdir()
            if directory.is_dir() and directory.name.isdigit()
        ]
    )

    if not versions:
        raise RuntimeError("No Maya versions detected")

    return versions[-1]


def get_modules_dir(version_dir: Path) -> Path:
    """
    Ensure modules directory exists
    """

    modules_dir = version_dir / "modules"
    modules_dir.mkdir(exist_ok=True)

    return modules_dir


def write_module_file(modules_dir: Path):
    project_root = Path(__file__).resolve().parents[1]
    module_path = modules_dir / f"{MODULE_NAME}.mod"

    if module_path.exists():
        response = (
            input(f"{module_path} already exists. Replace? [y/N]: ").strip().lower()
        )

        if response != "y":
            print("Installation cancelled")
            return

    print(f"Writing module file to: {module_path}")

    with open(module_path, "w") as file:
        file.write(f"+ {MODULE_NAME} {MODULE_VERSION} {project_root}\n")
        file.write("PYTHONPATH +:= .\n")
        file.write("PYTHONPATH +:= maya_module/plug-ins/modules\n")
        file.write("MAYA_PLUG_IN_PATH +:= maya_module/plug-ins\n")
        file.write("XBMLANGPATH +:= maya_module/plug-ins/icons\n")
        file.write("MAYA_SCRIPT_PATH +:= maya_module/scripts\n")

    print(f"Module {MODULE_NAME} installed successfully")


def install_module():
    root = get_maya_root()
    version_dir = get_maya_version(root)
    modules_dir = get_modules_dir(version_dir)
    write_module_file(modules_dir)


if __name__ == "__main__":
    try:
        install_module()
    except Exception as e:
        print(f"Module {MODULE_NAME} installation failed: {e}")
        sys.exit(os.EX_CONFIG)

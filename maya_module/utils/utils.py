import platform
import maya.mel as mel
import maya.cmds as cmds

from pathlib import Path


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

    Args:
        root (Path): The root directory to search for Maya versions
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

    Args:
        version_dir (Path): The Maya version directory to create the modules folder in
    """

    modules_dir = version_dir / "modules"
    modules_dir.mkdir(exist_ok=True)

    return modules_dir


def get_main_shelves_layout() -> str:
    """
    Return Maya top level shelf layout
    """
    return mel.eval("$tmpVar=$gShelfTopLevel")


def get_shelf_button(shelf_name: str, button_label: str) -> str | None:
    """
    Find existing shelf button by label

    Args:
        shelf_name (str): The name of the shelf to search for the button in
        button_label (str): The label of the button to find
    """

    buttons = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []

    for btn in buttons:
        if cmds.objectTypeUI(btn) != "shelfButton":
            continue

        label = cmds.shelfButton(btn, query=True, label=True)

        if label == button_label:
            return btn
    return None

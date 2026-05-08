"""
Maya logging utilities.
"""


def _maya_available() -> object | None:
    """
    Determine if Maya's OpenMaya API is available and return it if so, otherwise return None
    """

    try:
        import maya.api.OpenMaya as om

        return om
    except Exception:
        return None


def info(message: str) -> None:
    """
    Log an informational message to Maya's script editor if available, otherwise print it to the console

    Args:
        message (str): The message to log
    """

    om = _maya_available()

    if om:
        om.MGlobal.displayInfo(message)
    else:
        print(message)


def warning(message: str) -> None:
    """
    Log a warning message to Maya's script editor if available, otherwise print it to the console

    Args:
        message (str): The message to log
    """

    om = _maya_available()

    if om:
        om.MGlobal.displayWarning(message)
    else:
        print(f"WARNING: {message}")


def error(message: str) -> None:
    """
    Log an error message to Maya's script editor if available, otherwise print it to the console

    Args:
        message (str): The message to log
    """

    om = _maya_available()

    if om:
        om.MGlobal.displayError(message)
    else:
        print(f"ERROR: {message}")

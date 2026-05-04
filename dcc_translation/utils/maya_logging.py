"""
Maya logging utilities.
"""

def _maya_available():
    try:
        import maya.api.OpenMaya as om
        return om
    except Exception:
        return None


def info(message):
    om = _maya_available()

    if om:
        om.MGlobal.displayInfo(message)
    else:
        print(message)


def warning(message):
    om = _maya_available()

    if om:
        om.MGlobal.displayWarning(message)
    else:
        print(f"WARNING: {message}")


def error(message):
    om = _maya_available()

    if om:
        om.MGlobal.displayError(message)
    else:
        print(f"ERROR: {message}")
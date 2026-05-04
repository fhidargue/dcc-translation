import pytest


@pytest.fixture(scope="session")
def maya_session():
    """Start Maya standalone only when requested by a test"""
    import maya.standalone

    try:
        maya.standalone.initialize(name="python")
    except RuntimeError:
        pass

    yield

    try:
        maya.standalone.uninitialize()
    except Exception:
        pass

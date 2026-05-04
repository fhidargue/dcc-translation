import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter

pytestmark = pytest.mark.maya


def test_rotate_pivot(maya_session):
    import maya.cmds as cmds

    cube = cmds.group(empty=True, name="cube")

    # Set rotate pivot
    cmds.xform(cube, rotatePivot=[1, 2, 3], worldSpace=False)

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    cube_node = next(node for node in nodes if node.name == cube)

    assert cube_node.metadata["maya"]["rotatePivot"] == [1, 2, 3]


def test_rotate_order(maya_session):
    import maya.cmds as cmds

    cube = cmds.group(empty=True, name="cube")

    # Set rotate order index 3, XZY
    cmds.setAttr(f"{cube}.rotateOrder", 3)

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    cube_node = next(node for node in nodes if node.name == cube)

    assert cube_node.metadata["maya"]["rotateOrder"] == "xzy"


def test_metadata_exists(maya_session):
    import maya.cmds as cmds

    cube = cmds.group(empty=True, name="cube")

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    cube_node = next(node for node in nodes if node.name == cube)

    assert "maya" in cube_node.metadata

import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter

pytestmark = pytest.mark.maya


def test_visible_node(maya_session):
    import maya.cmds as cmds

    cube = cmds.group(empty=True, name="cube")

    cmds.setAttr(f"{cube}.visibility", True)

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    cube_node = next(node for node in nodes if node.name == cube)

    assert cube_node.metadata["maya"]["visibility"] is True


def test_hidden_node(maya_session):
    import maya.cmds as cmds

    cube = cmds.group(empty=True, name="cube")

    cmds.setAttr(f"{cube}.visibility", False)

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    cube_node = next(node for node in nodes if node.name == cube)

    assert cube_node.metadata["maya"]["visibility"] is False


def test_override_visibility(maya_session):
    import maya.cmds as cmds

    cube = cmds.group(empty=True, name="cube")

    # Enable override visibility
    cmds.setAttr(f"{cube}.overrideEnabled", True)
    cmds.setAttr(f"{cube}.overrideVisibility", False)

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    cube_node = next(node for node in nodes if node.name == cube)

    assert cube_node.metadata["maya"]["visibility"] is False

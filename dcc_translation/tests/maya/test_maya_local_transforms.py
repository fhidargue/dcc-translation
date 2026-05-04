import numpy as np
import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter

pytestmark = pytest.mark.maya


def test_local_transform(maya_session):
    import maya.cmds as cmds

    root = cmds.group(empty=True, name="root")

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    root_node = next(node for node in nodes if node.name == root)

    assert np.array_equal(root_node.transform, np.identity(4))


def test_child_transform_is_local(maya_session):
    import maya.cmds as cmds

    root = cmds.group(empty=True, name="root")
    child = cmds.group(empty=True, name="child", parent=root)

    # Apply scale so matrix differs from identity
    cmds.scale(2, 1, 1, child)

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    root_node = next(node for node in nodes if node.name == root)
    child_node = root_node.children[0]

    assert child_node.transform[0][0] == 2


def test_worldspace_flag_not_used(maya_session):
    import maya.cmds as cmds

    root = cmds.group(empty=True, name="root")  # noqa: F841

    original_xform = cmds.xform

    def wrapped_xform(*args, **kwargs):
        # Ensure adapter never requests worldSpace=True
        assert kwargs.get("worldSpace") is not True
        return original_xform(*args, **kwargs)

    cmds.xform = wrapped_xform

    try:
        adapter = MayaAdapter()
        adapter.extract_scene_nodes()
    finally:
        cmds.xform = original_xform

import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter

pytestmark = pytest.mark.maya


def test_intermediate_shape_filtered(maya_session):
    import maya.cmds as cmds

    cube = cmds.polyCube(name="cube")[0]

    shape = cmds.listRelatives(cube, shapes=True)[0]

    # Mark the only shape intermediate
    cmds.setAttr(f"{shape}.intermediateObject", True)

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    cube_node = next(node for node in nodes if node.name == cube)

    assert cube_node.mesh_path is None

import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter

pytestmark = pytest.mark.maya


def test_multiple_uv_sets(maya_session):
    import maya.cmds as cmds

    mesh = cmds.polyPlane(
        name="meshA",
        width=1,
        height=1,
        subdivisionsX=1,
        subdivisionsY=1,
    )[0]

    shape = cmds.listRelatives(mesh, shapes=True)[0]

    # Create second UV set
    cmds.polyUVSet(shape, create=True, uvSet="lightmap")

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    mesh_node = next(node for node in nodes if node.name == mesh)

    assert "map1" in mesh_node.uv_sets
    assert "lightmap" in mesh_node.uv_sets

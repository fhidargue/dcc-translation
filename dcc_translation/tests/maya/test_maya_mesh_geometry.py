import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter

pytestmark = pytest.mark.maya


def test_mesh_geometry_extraction(maya_session):
    import maya.cmds as cmds

    mesh = cmds.polyPlane(
        name="meshA",
        width=1,
        height=1,
        subdivisionsX=1,
        subdivisionsY=1,
    )[0]

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    mesh_node = next(node for node in nodes if node.name == mesh)

    assert mesh_node.points is not None
    assert len(mesh_node.points) == 4

    assert mesh_node.face_counts == [4]
    assert sorted(mesh_node.face_indices) == [0, 1, 2, 3]

import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter

pytestmark = pytest.mark.maya


def test_detect_shared_mesh_instance(maya_session):
    import maya.cmds as cmds

    chair_A = cmds.polyCube(name="chair_A")[0]
    chair_B = cmds.instance(chair_A, name="chair_B")[0]

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    instance_nodes = [
        node for node in nodes if "instanceOf" in node.metadata.get("maya", {})
    ]

    assert len(instance_nodes) == 1
    assert instance_nodes[0].name == chair_B
    assert instance_nodes[0].metadata["maya"]["instanceOf"].endswith("chair_A")


def test_first_mesh_is_canonical(maya_session):
    import maya.cmds as cmds

    chair_A = cmds.polyCube(name="chair_A")[0]
    chair_B = cmds.instance(chair_A, name="chair_B")[0]

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    canonical_nodes = [
        node
        for node in nodes
        if node.name in [chair_A, chair_B]
        and "instanceOf" not in node.metadata.get("maya", {})
    ]

    assert len(canonical_nodes) == 1
    assert canonical_nodes[0].name == chair_A

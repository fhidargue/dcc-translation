import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter


pytestmark = pytest.mark.maya


def test_transform_mesh_shape(maya_session):
    import maya.cmds as cmds

    cube = cmds.polyCube(name="cube")[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    node = next(n for n in nodes if n.name == cube)

    assert node.node_type == "mesh"
    assert node.mesh_path.endswith(shape)


def test_select_first_mesh(maya_session):
    import maya.cmds as cmds

    cube = cmds.polyCube(name="cube")[0]

    original_shape = cmds.listRelatives(cube, shapes=True)[0]
    duplicate_shape = cmds.duplicate(original_shape, name="cubeShapeOrig")[0]

    # Make duplicate intermediate
    cmds.setAttr(f"{duplicate_shape}.intermediateObject", True)

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    node = next(n for n in nodes if n.name == cube)

    print("node: ", node.mesh_path)

    assert node.mesh_path.endswith("cube3Shape")


def test_transform_without_mesh(maya_session):
    import maya.cmds as cmds

    group = cmds.group(empty=True, name="group")

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    node = next(n for n in nodes if n.name == group)

    assert node.node_type == "transform"
    assert node.mesh_path is None

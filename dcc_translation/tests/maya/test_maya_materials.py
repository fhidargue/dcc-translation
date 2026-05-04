import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter


pytestmark = pytest.mark.maya


def test_extract_material(maya_session):
    import maya.cmds as cmds

    cube = cmds.polyCube(name="cube")[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]

    material = cmds.shadingNode("lambert", asShader=True, name="lambert_test")
    sg = cmds.sets(
        renderable=True, noSurfaceShader=True, empty=True, name="lambert_testSG"
    )

    cmds.connectAttr(f"{material}.outColor", f"{sg}.surfaceShader")
    cmds.sets(shape, edit=True, forceElement=sg)

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    cube_node = next(node for node in nodes if node.name == cube)

    assert cube_node.metadata["maya"]["material"] == "lambert_test"

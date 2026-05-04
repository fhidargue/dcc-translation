import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter


@pytest.mark.maya
def test_extract_texture_path(maya_session):
    import maya.cmds as cmds

    cube = cmds.polyCube(name="cube")[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]
    material = cmds.shadingNode("lambert", asShader=True, name="lambert_test")
    specular = cmds.sets(
        renderable=True, noSurfaceShader=True, empty=True, name="lambert_testSG"
    )

    cmds.connectAttr(f"{material}.outColor", f"{specular}.surfaceShader")
    cmds.sets(shape, edit=True, forceElement=specular)

    # Create file texture node
    file_node = cmds.shadingNode("file", asTexture=True, name="fileTexture_test")
    cmds.setAttr(f"{file_node}.fileTextureName", "/textures/wood.png", type="string")

    # Connect texture to material color
    cmds.connectAttr(f"{file_node}.outColor", f"{material}.color")

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    cube_node = next(node for node in nodes if node.name == cube)

    assert (
        cube_node.metadata["maya"]["textures"]["diffuseColor"] == "/textures/wood.png"
    )

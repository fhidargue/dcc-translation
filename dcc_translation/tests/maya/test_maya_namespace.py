import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter

pytestmark = pytest.mark.maya


def test_namespace_extracted(maya_session):
    import maya.cmds as cmds

    # Create namespace hierarchy
    cmds.namespace(add="kitchen")
    cmds.namespace(add="setA", parent="kitchen")

    cmds.namespace(set="kitchen:setA")
    chair = cmds.group(empty=True, name="chair_01")  # noqa: F841
    cmds.namespace(set=":")

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    chair_node = next(node for node in nodes if node.name.endswith("chair_01"))

    assert chair_node.metadata["maya"]["namespace"] == "kitchen:setA"


def test_shortname_extracted(maya_session):
    import maya.cmds as cmds

    cmds.namespace(add="props")
    cmds.namespace(add="setB", parent="props")

    cmds.namespace(set="props:setB")
    plate = cmds.group(empty=True, name="plate_03")  # noqa: F841
    cmds.namespace(set=":")

    adapter = MayaAdapter()
    nodes = adapter.extract_scene_nodes()

    plate_node = next(node for node in nodes if node.name.endswith("plate_03"))

    assert plate_node.metadata["maya"]["shortName"] == "plate_03"

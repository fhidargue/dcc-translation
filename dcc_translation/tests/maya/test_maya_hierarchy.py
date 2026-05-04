import pytest

pytestmark = pytest.mark.maya


def test_single_transform_parent(maya_session):
    import maya.cmds as cmds

    parent = cmds.group(empty=True, name="parent")
    child = cmds.group(empty=True, name="child")

    cmds.parent(child, parent)

    assert cmds.listRelatives(child, parent=True)[0] == parent


def test_multiple_children_parenting(maya_session):
    import maya.cmds as cmds

    parent = cmds.group(empty=True, name="parent")

    children = [cmds.group(empty=True, name=f"child_{i}") for i in range(3)]

    cmds.parent(children, parent)
    result = cmds.listRelatives(parent, children=True)

    assert set(result) == set(children)

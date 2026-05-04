import pytest

from dcc_translation.adapters.maya_adapter import MayaAdapter

pytestmark = pytest.mark.maya


def test_root_transforms(maya_session):
    import maya.cmds as cmds

    root = cmds.group(empty=True, name="root")

    adapter = MayaAdapter()
    roots = adapter._get_root_transforms()

    assert any(r.endswith(root) for r in roots)


def test_root_transforms_multiple_roots(maya_session):
    import maya.cmds as cmds

    A = cmds.group(empty=True, name="A")
    B = cmds.group(empty=True, name="B")

    adapter = MayaAdapter()
    roots = adapter._get_root_transforms()

    assert all(any(r.endswith(name) for r in roots) for name in [A, B])


def test_root_transforms_excludes_children(maya_session):
    import maya.cmds as cmds

    root = cmds.group(empty=True, name="root")
    cmds.group(empty=True, name="child", parent=root)

    adapter = MayaAdapter()
    roots = adapter._get_root_transforms()

    assert any(r.endswith(root) for r in roots)
    assert not any(r.endswith("child") for r in roots)

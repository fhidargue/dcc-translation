import numpy as np
import pytest
from dcc_translation.core.scene_graph import SceneNode

pytestmark = pytest.mark.local


def test_scene_node_defaults():
    node = SceneNode(
        name="root",
        node_type="transform",
        transform=np.identity(4),
    )

    assert node.name == "root"
    assert node.node_type == "transform"
    assert node.mesh_path is None
    assert node.children == []
    assert node.uuid is not None


def test_scene_node_relationship():
    parent = SceneNode(
        name="parent",
        node_type="transform",
        transform=np.identity(4),
    )

    child = SceneNode(
        name="child",
        node_type="mesh",
        transform=np.identity(4),
        mesh_path="shape",
    )

    parent.add_child(child)

    assert len(parent.children) == 1
    assert parent.children[0].name == "child"


def test_scene_node_mesh_type():
    node = SceneNode(
        name="cube",
        node_type="mesh",
        transform=np.identity(4),
        mesh_path="cubeShape",
    )

    assert node.node_type == "mesh"
    assert node.mesh_path == "cubeShape"


def test_scene_node_matrix_shape():
    node = SceneNode(
        name="obj",
        node_type="transform",
        transform=np.identity(4),
    )

    assert node.transform.shape == (4, 4)


def test_scene_node_uuid():
    node = SceneNode(
        name="node",
        node_type="transform",
        transform=np.identity(4),
    )

    assert isinstance(node.uuid, str)
    assert len(node.uuid) > 10


def test_transform_no_mesh_path():
    node = SceneNode(
        name="group",
        node_type="transform",
        transform=np.identity(4),
    )

    assert node.mesh_path is None

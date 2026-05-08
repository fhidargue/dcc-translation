import pytest

from dcc_translation.core.scene_graph import SceneNode

pytestmark = pytest.mark.local


def test_scene_node_creation():
    """
    Scene node initializes correctly
    """

    node = SceneNode(
        name="Kitchen",
        node_type="transform",
    )

    assert node.name == "Kitchen"
    assert node.node_type == "transform"
    assert node.children == []


def test_scene_node_transform_storage():
    """
    Scene node stores transforms
    """

    transform = {
        "translate": [1, 2, 3],
        "rotate": [0, 90, 0],
        "scale": [1, 1, 1],
    }

    node = SceneNode(
        name="Cube",
        node_type="mesh",
        transform=transform,
    )

    assert node.transform == transform


def test_scene_node_metadata():
    """
    Scene node stores metadata
    """

    metadata = {
        "publish_id": "1234",
        "source": "maya",
    }

    node = SceneNode(
        name="Chair",
        node_type="mesh",
        metadata=metadata,
    )

    assert node.metadata["publish_id"] == "1234"


def test_scene_node_mesh_path():
    """
    Scene node stores mesh path
    """

    node = SceneNode(
        name="Cup",
        node_type="mesh",
        mesh_path="/geo/cup.obj",
    )

    assert node.mesh_path == "/geo/cup.obj"


def test_scene_node_add_child():
    """
    Child nodes can be added
    """

    parent = SceneNode(
        name="Kitchen",
        node_type="transform",
    )

    child = SceneNode(
        name="Chair",
        node_type="mesh",
    )

    parent.children.append(child)

    assert len(parent.children) == 1
    assert parent.children[0].name == "Chair"


def test_scene_graph_nested_hierarchy():
    """
    Nested hierarchy stores correctly
    """

    root = SceneNode(
        name="Root",
        node_type="transform",
    )

    kitchen = SceneNode(
        name="Kitchen",
        node_type="transform",
    )

    chair = SceneNode(
        name="Chair",
        node_type="mesh",
    )

    kitchen.children.append(chair)
    root.children.append(kitchen)

    assert root.children[0].children[0].name == "Chair"


def test_scene_node_visibility_metadata():
    """
    Visibility metadata stores correctly
    """

    node = SceneNode(
        name="Lamp",
        node_type="mesh",
        metadata={
            "visibility": False,
        },
    )

    assert node.metadata["visibility"] is False


def test_scene_node_instance_metadata():
    """
    Instancing metadata stores correctly
    """

    node = SceneNode(
        name="ChairInstance",
        node_type="mesh",
        metadata={
            "maya": {
                "instanceOf": "ChairPrototype",
            },
        },
    )

    assert node.metadata["maya"]["instanceOf"] == "ChairPrototype"


def test_scene_node_empty_metadata_defaults():
    """
    Metadata defaults safely
    """

    node = SceneNode(
        name="Cube",
        node_type="mesh",
    )

    assert isinstance(node.metadata, dict)
    assert node.metadata == {}


def test_scene_node_children_default():
    """
    Children list initializes safely
    """

    node = SceneNode(
        name="Root",
        node_type="transform",
    )

    assert isinstance(node.children, list)
    assert node.children == []


def test_scene_node_multiple_children():
    """
    Multiple children store correctly
    """

    root = SceneNode(
        name="Scene",
        node_type="transform",
    )

    for name in [
        "Chair",
        "Table",
        "Lamp",
    ]:
        root.children.append(
            SceneNode(
                name=name,
                node_type="mesh",
            )
        )

    assert len(root.children) == 3


def test_scene_node_custom_attributes():
    """
    Custom metadata attributes persist
    """

    node = SceneNode(
        name="Asset",
        node_type="mesh",
        metadata={
            "custom": {
                "lod": 1,
                "material": "wood",
            },
        },
    )

    assert node.metadata["custom"]["lod"] == 1
    assert node.metadata["custom"]["material"] == "wood"

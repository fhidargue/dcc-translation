from pathlib import Path
import numpy as np
import pytest

from dcc_translation.core.validator import (
    ValidationProfileLoader,
    SceneValidator,
)
from dcc_translation.core.scene_graph import SceneNode

pytestmark = pytest.mark.local


@pytest.fixture
def identity_matrix():
    return np.identity(4)


@pytest.fixture
def base_rules():
    return {
        "require_frozen_transforms": {"enabled": False},
        "require_geometry": {"enabled": False},
    }


def make_node(
    name="cube",
    node_type="mesh",
    transform=None,
    mesh_path="shape",
):
    if transform is None:
        transform = np.identity(4)

    return SceneNode(
        name=name,
        node_type=node_type,
        transform=transform,
        mesh_path=mesh_path,
    )


def test_load_validation_profile():
    project_root = Path(__file__).resolve().parents[3]
    profile_path = project_root / "validation_profiles" / "maya_to_unreal.yml"
    rules = ValidationProfileLoader.load_file(profile_path)

    assert rules["pipeline_target"] == "unreal"


def test_non_frozen_transform(identity_matrix):
    rules = {
        "require_frozen_transforms": {
            "enabled": True,
            "severity": "error",
        },
        "require_geometry": {"enabled": False},
    }

    node = make_node(transform=np.ones((4, 4)))
    report = SceneValidator(rules).validate([node])

    assert report.errors


def test_missing_geometry(identity_matrix):
    rules = {
        "require_frozen_transforms": {"enabled": False},
        "require_geometry": {
            "enabled": True,
            "severity": "error",
        },
    }

    node = make_node(mesh_path=None)
    report = SceneValidator(rules).validate([node])

    assert report.errors


def test_invalid_node_type(base_rules):
    rules = base_rules | {"allowed_node_types": ["mesh"]}
    node = make_node(node_type="camera")
    report = SceneValidator(rules).validate([node])

    assert report.errors


def test_invalid_node_name(base_rules):
    rules = base_rules | {
        "enforce_naming_convention": {
            "enabled": True,
            "severity": "warning",
        }
    }

    node = make_node(name="bad-name!")
    report = SceneValidator(rules).validate([node])

    assert report.warnings


def test_duplicate_names(base_rules):
    node1 = make_node(name="cube")
    node2 = make_node(name="cube")

    report = SceneValidator(base_rules).validate([node1, node2])

    assert report.errors


def test_invalid_matrix_size(base_rules):
    node = make_node(transform=[1, 2, 3])
    report = SceneValidator(base_rules).validate([node])

    assert report.errors

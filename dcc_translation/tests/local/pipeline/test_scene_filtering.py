from dcc_translation.core.scene_graph import SceneNode
from dcc_translation.core.validator import SceneValidator
import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_invalid_nodes_removed():
    rules = {
        "require_frozen_transforms": {"enabled": False},
        "require_geometry": {
            "enabled": True,
            "severity": "error",
        },
    }

    valid_node = SceneNode(
        "valid_mesh",
        "mesh",
        np.identity(4),
        mesh_path="shape",
    )

    invalid_node = SceneNode(
        "invalid_mesh",
        "mesh",
        np.identity(4),
        mesh_path=None,
    )

    validator = SceneValidator(rules)
    validator.validate([valid_node, invalid_node])

    filtered = validator.filter_valid_nodes([valid_node, invalid_node])

    assert len(filtered) == 1
    assert filtered[0].name == "valid_mesh"

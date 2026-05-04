from dcc_translation.core.scene_graph import SceneNode
from dcc_translation.core.validator import SceneValidator

import pytest

pytestmark = pytest.mark.local


def test_validator_missing_geometry():
    rules = {
        "require_frozen_transforms": {"enabled": False},
        "require_geometry": {
            "enabled": True,
            "severity": "error",
        },
    }

    node = SceneNode(
        name="cube",
        node_type="mesh",
        transform=[1.0, 0.0, 0.0, 0.0],
        mesh_path=None,
    )

    validator = SceneValidator(rules)

    report = validator.validate([node])

    assert report.blocking

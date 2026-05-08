from dcc_translation.exporter.usd_exporter import USDExporter
from dcc_translation.core.scene_graph import SceneNode

import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_instance_reuses_existing_mesh(tmp_path):
    output = tmp_path / "scene.usda"

    base = SceneNode(
        name="chair_A",
        node_type="mesh",
        transform=np.identity(4),
    )

    instance = SceneNode(
        name="chair_B",
        node_type="mesh",
        transform=np.identity(4),
        metadata={"maya": {"instanceOf": "chair_A"}},
    )

    exporter = USDExporter(str(output))
    exporter.export([base, instance])

    content = output.read_text()

    assert content.count("def Mesh") == 1

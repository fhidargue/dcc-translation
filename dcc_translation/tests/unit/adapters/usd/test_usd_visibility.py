from dcc_translation.exporter.usd_exporter import USDExporter
from dcc_translation.core.scene_graph import SceneNode

import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_hidden_node(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="cube",
        node_type="transform",
        transform=np.identity(4),
        metadata={"maya": {"visibility": False}},
    )

    exporter = USDExporter(str(output))
    exporter.export([node])

    content = output.read_text()

    assert 'visibility = "invisible"' in content

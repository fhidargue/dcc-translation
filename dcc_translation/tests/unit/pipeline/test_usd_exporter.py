from dcc_translation.core.scene_graph import SceneNode
from dcc_translation.exporter.usd_exporter import USDExporter
import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_usd_export(tmp_path):
    output_file = tmp_path / "scene.usd"
    node = SceneNode(
        name="cube",
        node_type="mesh",
        transform=np.identity(4),
        mesh_path="cubeShape",
    )

    exporter = USDExporter(str(output_file))
    exporter.export([node])

    assert output_file.exists()

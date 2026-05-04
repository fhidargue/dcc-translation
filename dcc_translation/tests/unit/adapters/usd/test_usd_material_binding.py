import pytest
import numpy as np

from dcc_translation.exporter.usd_exporter import USDExporter
from dcc_translation.core.scene_graph import SceneNode

pytestmark = pytest.mark.local


def test_material_binding(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="table",
        node_type="mesh",
        transform=np.identity(4),
        metadata={"maya": {"material": "WoodMaterial"}},
    )

    exporter = USDExporter(str(output))
    exporter.export([node])

    text = output.read_text()

    assert "rel material:binding" in text
    assert "/Materials/WoodMaterial" in text

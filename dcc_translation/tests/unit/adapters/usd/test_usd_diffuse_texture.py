import pytest
import numpy as np

from dcc_translation.exporter.usd_exporter import USDExporter
from dcc_translation.core.scene_graph import SceneNode

pytestmark = pytest.mark.local


def test_diffuse_texture_export(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="cabinet",
        node_type="mesh",
        transform=np.identity(4),
        metadata={
            "maya": {
                "material": "WoodMaterial",
                "textures": {"diffuseColor": "wood.png"},
            }
        },
    )

    exporter = USDExporter(str(output))
    exporter.export([node])

    text = output.read_text()

    assert "UsdPreviewSurface" in text
    assert "UsdUVTexture" in text
    assert "wood.png" in text

import numpy as np
from dcc_translation.core.scene_graph import SceneNode
from dcc_translation.exporter.usd_exporter import USDExporter

import pytest

pytestmark = pytest.mark.local


def test_texture_export(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="cabinet",
        node_type="mesh",
        transform=np.identity(4),
        metadata={
            "maya": {
                "material": "CabinetMaterial",
                "textures": {
                    "diffuseColor": "albedo.png",
                    "normal": "normal.png",
                    "roughness": "rough.png",
                    "metallic": "metal.png",
                },
            }
        },
    )

    exporter = USDExporter(str(output))
    exporter.export([node])

    text = output.read_text()

    assert "albedo.png" in text
    assert "normal.png" in text
    assert "rough.png" in text
    assert "metal.png" in text

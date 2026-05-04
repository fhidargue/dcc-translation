from dcc_translation.exporter.usd_exporter import USDExporter
from dcc_translation.core.scene_graph import SceneNode

import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_normals_and_uvs(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="quad",
        node_type="mesh",
        transform=np.identity(4),
        points=[
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
            (0, 1, 0),
        ],
        face_counts=[4],
        face_indices=[0, 1, 2, 3],
        normals=[
            (0, 0, 1),
            (0, 0, 1),
            (0, 0, 1),
            (0, 0, 1),
        ],
        uv_sets={
            "map1": [(0, 0)],
        },
    )

    exporter = USDExporter(str(output))
    exporter.export([node])
    text = output.read_text()

    assert "normal3f[]" in text
    assert "primvars:st" in text


def test_multiple_uv_sets(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="quad",
        node_type="mesh",
        transform=np.identity(4),
        points=[(0, 0, 0)],
        face_counts=[1],
        face_indices=[0],
        uv_sets={"map1": [(0, 0)], "lightmap": [(1, 1)]},
    )

    exporter = USDExporter(str(output))
    exporter.export([node])

    text = output.read_text()

    assert "primvars:st" in text
    assert "lightmap" in text

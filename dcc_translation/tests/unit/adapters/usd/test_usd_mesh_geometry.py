from dcc_translation.exporter.usd_exporter import USDExporter
from dcc_translation.core.scene_graph import SceneNode

import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_mesh_points(tmp_path):
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
    )

    exporter = USDExporter(str(output))
    exporter.export([node])

    text = output.read_text()

    assert "point3f[] points" in text
    assert "int[] faceVertexCounts" in text
    assert "int[] faceVertexIndices" in text


def test_mesh_topology(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="triangle",
        node_type="mesh",
        transform=np.identity(4),
        points=[
            (0, 0, 0),
            (1, 0, 0),
            (0, 1, 0),
        ],
        face_counts=[3],
        face_indices=[0, 1, 2],
    )

    exporter = USDExporter(str(output))
    exporter.export([node])
    text = output.read_text()

    assert "faceVertexCounts = [3]" in text
    assert "faceVertexIndices = [0, 1, 2]" in text

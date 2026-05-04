from dcc_translation.exporter.usd_exporter import USDExporter
from dcc_translation.core.scene_graph import SceneNode

import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_rotate_pivot(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="door",
        node_type="transform",
        transform=np.identity(4),
        metadata={"maya": {"rotatePivot": [1, 2, 3]}},
    )

    exporter = USDExporter(str(output), "houdini")
    exporter.export([node])

    text = output.read_text()

    print("text: ", text)

    assert "xformOp:translate:pivot" in text


def test_scale_pivot(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="cabinet",
        node_type="transform",
        transform=np.identity(4),
        metadata={"maya": {"scalePivot": [4, 5, 6]}},
    )

    exporter = USDExporter(str(output), "houdini")
    exporter.export([node])

    text = output.read_text()

    assert "xformOp:translate:scalePivot" in text


def test_rotate_order(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="handle",
        node_type="transform",
        transform=np.identity(4),
        metadata={"maya": {"rotateOrder": 2}},
    )

    exporter = USDExporter(str(output))
    exporter.export([node])

    text = output.read_text()

    assert "maya_rotateOrder" in text

from dcc_translation.exporter.usd_exporter import USDExporter
from dcc_translation.core.scene_graph import SceneNode

import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_namespace(tmp_path):
    output = tmp_path / "scene.usda"

    node = SceneNode(
        name="chair_01",
        node_type="mesh",
        transform=np.identity(4),
        metadata={"maya": {"namespace": "kitchen:setA", "shortName": "chair_01"}},
    )

    exporter = USDExporter(str(output))
    exporter.export([node])

    content = output.read_text()

    assert "kitchen:setA" not in content
    assert 'def Mesh "chair_01"' in content


def test_namespace_removed_in_child_paths(tmp_path):
    output = tmp_path / "scene.usda"

    parent = SceneNode(
        name="parent",
        node_type="transform",
        transform=np.identity(4),
    )

    child = SceneNode(
        name="chair_01",
        node_type="mesh",
        transform=np.identity(4),
        metadata={"maya": {"namespace": "kitchen:setA", "shortName": "chair_01"}},
    )

    parent.add_child(child)

    exporter = USDExporter(str(output))
    exporter.export([parent])

    content = output.read_text()

    assert "kitchen:setA" not in content
    assert 'def Mesh "chair_01"' in content

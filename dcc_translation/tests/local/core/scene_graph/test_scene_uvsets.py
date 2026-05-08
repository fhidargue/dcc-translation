from dcc_translation.core.scene_graph import SceneNode

import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_scene_node_multiple_uv_sets():

    node = SceneNode(
        name="cube",
        node_type="mesh",
        transform=np.identity(4),
        uv_sets={"map1": [(0, 0), (1, 0)], "lightmap": [(0, 1), (1, 1)]},
    )

    assert "map1" in node.uv_sets
    assert "lightmap" in node.uv_sets

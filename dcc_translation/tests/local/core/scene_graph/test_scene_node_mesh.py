from dcc_translation.core.scene_graph import SceneNode

import numpy as np
import pytest

pytestmark = pytest.mark.local


def test_scene_node_mesh():
    node = SceneNode(
        name="cube",
        node_type="mesh",
        transform=np.identity(4),
        points=[(0, 0, 0)],
        face_counts=[4],
        face_indices=[0, 1, 2, 3],
    )

    assert node.points is not None
    assert node.face_counts == [4]
    assert node.face_indices == [0, 1, 2, 3]

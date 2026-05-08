from dcc_translation.adapters.base_adapter import DCCAdapter
from dcc_translation.core.scene_graph import SceneNode
from dcc_translation.utils.constants import DCC_MAYA

import numpy as np


class MockAdapter(DCCAdapter):
    """
    Test adapter that simulates a DCC scene
    """

    def get_source_dcc_name(self) -> str:
        return DCC_MAYA

    def get_scene_name(self) -> str:
        return "testing_scene.ma"

    def extract_scene_nodes(self, rules=None) -> list:
        return [
            SceneNode(
                name="cube1",
                node_type="mesh",
                transform=np.identity(4),
                mesh_path="cubeShape1",
            )
        ]

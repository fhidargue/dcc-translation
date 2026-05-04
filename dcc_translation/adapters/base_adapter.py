from abc import ABC, abstractmethod


class DCCAdapter(ABC):
    """
    Base adapter interface for all DCC integrations
    """

    @abstractmethod
    def extract_scene_nodes(self):
        """
        Extract SceneGraph nodes from the DCC scene

        Returns:
            list: List of SceneNode objects representing the scene hierarchy
        """
        pass

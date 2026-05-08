from typing import Optional, List
import uuid
import numpy as np

try:
    from pxr import Gf
except ImportError:
    Gf = None


class SceneNode:
    """
    Canonical SceneGraph node representation

    Attributes:
        uuid (str): Unique identifier for the node
        name (str): Name of the node
        node_type (str): Type of the node (e.g., "mesh", "light", "camera")
        transform (list): 4x4 transformation matrix as a flat list of 16 values
        mesh_path (str): Optional path to the mesh data if this node is a mesh
        metadata (dict): Additional metadata for the node
        children (list): List of child SceneNode instances
        parent (SceneNode): Reference to the parent SceneNode
        points: Optional list of vertex positions for mesh nodes
        face_counts: Optional list of face vertex counts for mesh nodes
        face_indices: Optional list of vertex indices for mesh faces
        normals: Optional list of vertex normals for mesh nodes
        uv_sets: Optional dictionary of UV sets for mesh nodes
    """

    def __init__(
        self,
        name: str,
        node_type: str,
        transform: Optional[list] = None,
        mesh_path: Optional[str] = None,
        metadata: Optional[dict] = None,
        points: Optional[list] = None,
        face_counts: Optional[list] = None,
        face_indices: Optional[list] = None,
        normals: Optional[list] = None,
        uv_sets: Optional[dict] = None,
    ):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.node_type = node_type
        self.transform = transform if transform is not None else np.identity(4).tolist()
        self.mesh_path = mesh_path
        self.metadata = metadata or {}
        self.children: List["SceneNode"] = []
        self.parent: Optional["SceneNode"] = None
        self.points = points
        self.face_counts = face_counts
        self.face_indices = face_indices
        self.normals = normals
        self.uv_sets = uv_sets or {}
        self.dependencies = []

    def add_child(self, child: "SceneNode") -> None:
        """
        Add a child node into the scene graph

        Args:
            child (SceneNode): The child node to be added
        """
        child.parent = self
        self.children.append(child)

    def get_matrix(self, as_usd: bool = True) -> Optional[np.ndarray]:
        """
        Returns transform matrix

        Args:
            as_usd (bool): If True and Gf is available, returns a Gf
        """

        if self.transform is None:
            return None

        matrix = np.array(self.transform, dtype=float)

        if matrix.size != 16:
            raise ValueError(f"{self.name}: transform must contain 16 values")

        matrix = matrix.reshape((4, 4))

        if as_usd and Gf:
            return Gf.Matrix4d(matrix.tolist())

        return matrix

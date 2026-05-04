from typing import Optional, List
import uuid
import numpy as np

try:
    from pxr import Gf
except ImportError:
    Gf = None


class SceneNode:
    """Canonical SceneGraph node representation"""

    def __init__(
        self,
        name: str,
        node_type: str,
        transform: list,
        mesh_path: Optional[str] = None,
        metadata: Optional[dict] = None,
        points=None,
        face_counts=None,
        face_indices=None,
        normals=None,
        uv_sets=None,
    ):
        self.uuid = str(uuid.uuid4())

        self.name = name
        self.node_type = node_type
        self.transform = transform
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

    def add_child(self, child: "SceneNode"):
        child.parent = self
        self.children.append(child)

    def get_matrix(self, as_usd=True):
        """
        Returns transform matrix
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

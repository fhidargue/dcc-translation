from dcc_translation.adapters.base_adapter import DCCAdapter
from dcc_translation.core.scene_graph import SceneNode
from dcc_translation.utils.constants import DCC_MAYA
from dcc_translation.utils.maya_utils import (
    safe_xform,
    extract_material_data,
    extract_normals,
    extract_points,
    extract_rotate_order,
    extract_topology,
    extract_uv_sets,
    extract_visibility,
    detect_instance,
    split_namespace,
)

import numpy as np
import os


class MayaAdapter(DCCAdapter):
    """
    Extracts hierarchical SceneGraph from Maya DAG

    Attributes:
        cmds: Reference to maya.cmds module (or None if not in Maya)
        om: Reference to maya.api.OpenMaya module (or None if not in Maya)
    """

    def __init__(self):
        try:
            import maya.cmds as cmds
            import maya.api.OpenMaya as om
        except ImportError:
            cmds = None
            om = None

        self.cmds = cmds
        self.om = om

    def get_source_dcc_name(self) -> str:
        return DCC_MAYA

    def get_scene_name(self) -> str:
        """
        Get Maya scene name
        """
        if self.cmds:
            path = self.cmds.file(query=True, sceneName=True)

            return os.path.basename(path) if path else "untitled_scene"
        return "unknown_scene"

    def extract_scene_nodes(self, rules=None) -> list:
        """
        Extract scene nodes from Maya

        Args:
            rules (dict, optional): Validation rules that may influence extraction
        """
        if self.cmds is None:
            raise RuntimeError("MayaAdapter requires Maya environment")

        # Exclude nodes from validation based on rules
        excluded = rules.get("exclude_node_types", []) if rules else []

        if isinstance(excluded, dict):
            self.excluded_types = set(excluded.keys())
        else:
            self.excluded_types = set(excluded)

        roots = self._get_root_transforms()
        scene_nodes = []

        # Set an empty mesh registry for the logging later
        self._mesh_registry = {}

        for root in roots:
            node = self._build_node_recursive(root)

            if node:
                scene_nodes.append(node)
        return scene_nodes

    def _get_root_transforms(self) -> list:
        """
        Get root transform nodes in the Maya scene (nodes without transform parents)
        """
        transforms = self.cmds.ls(type="transform", long=True)
        roots = []

        for node in transforms:
            parent = self.cmds.listRelatives(node, parent=True, type="transform")

            if not parent:
                roots.append(node)
        return roots

    def _build_node_recursive(self, transform: str) -> SceneNode:
        """
        Recursively build SceneNode from a Maya transform node, extracting geometry and metadata as needed

        Args:
            transform (str): Full path of the Maya transform node
        """
        excluded = getattr(self, "excluded_types", set())

        transform_type = self.cmds.nodeType(transform)
        if transform_type in excluded:
            return None

        shapes = self.cmds.listRelatives(transform, shapes=True, fullPath=True) or []
        shape_type_map = {shape: self.cmds.nodeType(shape) for shape in shapes}
        shape_types = set(shape_type_map.values())

        # Skip transforms whose shapes are excluded
        if shape_types and shape_types.issubset(excluded):
            return None

        # Transform matrix
        matrix = np.array(
            self.cmds.xform(transform, q=True, matrix=True, os=True)
        ).reshape((4, 4))

        # Obtain the local tranform attributes
        translate = self.cmds.getAttr(f"{transform}.translate")[0]
        rotate = self.cmds.getAttr(f"{transform}.rotate")[0]
        scale = self.cmds.getAttr(f"{transform}.scale")[0]

        # Mesh detection
        mesh_shapes = [
            shape
            for shape, transform in shape_type_map.items()
            if transform == "mesh"
            and not self.cmds.getAttr(f"{shape}.intermediateObject")
            and not shape.endswith("Orig")
        ]

        mesh_path = mesh_shapes[0] if mesh_shapes else None
        node_type = "mesh" if mesh_path else "transform"

        # Geometry extraction
        points = face_counts = face_indices = normals = None
        uv_sets = {}

        if mesh_path:
            points = extract_points(self, mesh_path)
            face_counts, face_indices = extract_topology(self, mesh_path)
            normals = extract_normals(self, mesh_path)
            uv_sets = extract_uv_sets(self, mesh_path)

        # Pivots
        rotate_pivot = safe_xform(self, transform, "rotatePivot")
        scale_pivot = safe_xform(self, transform, "scalePivot")

        # Rotation order
        rotate_order = extract_rotate_order(self, transform)

        # Visibility
        visibility = extract_visibility(self, transform)

        # Instancing
        instance_of = detect_instance(self, transform, mesh_path)

        # Naming
        namespace, short_name = split_namespace(transform)

        # Materials
        material_name, texture_paths = extract_material_data(self, mesh_path)

        # Metadata
        metadata = {
            "maya": {
                "rotateOrder": rotate_order,
                "visibility": visibility,
                "shortName": short_name,
                "translate": list(translate),
                "rotate": list(rotate),
                "scale": list(scale),
            }
        }

        if rotate_pivot:
            metadata["maya"]["rotatePivot"] = rotate_pivot

        if scale_pivot:
            metadata["maya"]["scalePivot"] = scale_pivot

        if instance_of:
            metadata["maya"]["instanceOf"] = instance_of

        if namespace:
            metadata["maya"]["namespace"] = namespace

        if material_name:
            metadata["maya"]["material"] = material_name

            if texture_paths:
                metadata["maya"]["textures"] = texture_paths

        node = SceneNode(
            name=short_name,
            node_type=node_type,
            transform=matrix,
            mesh_path=mesh_path,
            metadata=metadata,
            points=points,
            face_counts=face_counts,
            face_indices=face_indices,
            normals=normals,
            uv_sets=uv_sets,
        )

        # Node recursion
        children = (
            self.cmds.listRelatives(
                transform,
                children=True,
                type="transform",
                fullPath=True,
            )
            or []
        )

        for child in children:
            child_node = self._build_node_recursive(child)
            if child_node:
                node.add_child(child_node)

        return node

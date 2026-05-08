from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import yaml
import re

from dcc_translation.core.scene_graph import SceneNode


class ValidationProfileLoader:
    """
    Loads YAML validation profiles for pipeline execution
    """

    @staticmethod
    def load_file(profile_path: str) -> dict:
        """
        Load validation profile from a YAML file

        Args:
            profile_path (str): Path to the validation profile file
        """
        path = Path(profile_path)

        if not path.exists():
            raise FileNotFoundError(f"Validation profile not found: {profile_path}")

        with open(path, "r") as file:
            return yaml.safe_load(file)


@dataclass
class ValidationReport:
    """
    Stores validation results with severity awareness

    Attributes:
        errors (list[str]): List of error messages
        warnings (list[str]): List of warning messages
        invalid_nodes (set[str]): Set of node names that failed validation
    """

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    invalid_nodes: set[str] = field(default_factory=set)

    def error(self, message: str, node_name: str | None = None) -> None:
        """
        Record an error message and optionally mark a node as invalid

        Args:
            message (str): The error message to record
            node_name (str | None): Optional name of the node associated with the error
        """
        self.errors.append(message)

        if node_name:
            self.invalid_nodes.add(node_name)

    def warning(self, message: str, node_name: str | None = None) -> None:
        """
        Record a warning message

        Args:
            message (str): The warning message to record
            node_name (str | None): Optional name of the node associated with the warning
        """
        self.warnings.append(message)

        if node_name:
            self.invalid_nodes.add(node_name)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def blocking(self) -> bool:
        return len(self.errors) > 0


class SceneValidator:
    """
    Executes rule-based validation using YAML profiles

    Attributes:
        rules (dict): Validation rules loaded from the YAML profile
        report (ValidationReport): Object to store validation results
        excluded_types (set): Set of node types to exclude from validation
        allow_empty_transforms (bool): Whether to allow transform nodes without geometry
        ignore_transform_geometry (bool): Whether to ignore missing geometry on transform nodes
    """

    def __init__(self, rules: dict):
        self.rules = rules
        self.report = ValidationReport()

        self.excluded_types = set(rules.get("exclude_node_types", []))

        self.allow_empty_transforms = rules.get("allow_empty_transforms", False)

        self.ignore_transform_geometry = rules.get("require_geometry", {}).get(
            "ignore_transforms_without_shapes", False
        )

    def validate(self, scene_nodes: list) -> ValidationReport:
        """
        Validate a list of scene nodes against the loaded rules

        Args:
            scene_nodes (list): List of SceneNode instances to validate
        """
        for node in scene_nodes:
            self._validate_node_recursive(node)

        return self.report

    def _validate_node_recursive(
        self,
        node: SceneNode,
    ) -> None:
        """
        Recursively validate SceneGraph nodes

        Args:
            node: SceneNode instance to validate
        """

        if node.node_type not in self.excluded_types:
            self._validate_node(node)

        for child in node.children:
            self._validate_node_recursive(child)

    def _validate_node(self, node: SceneNode) -> None:
        """
        Validate individual scene node

        Args:
            node: SceneNode instance to validate
        """

        frozen_rule = self.rules.get(
            "require_frozen_transforms",
            {},
        )

        geometry_rule = self.rules.get(
            "require_geometry",
            {},
        )

        naming_rule = self.rules.get(
            "enforce_naming_convention",
            {},
        )

        allowed_types_rule = self.rules.get(
            "allowed_node_types",
        )

        if frozen_rule.get("enabled", False):
            self._check_frozen_transforms(node)

        if geometry_rule.get("enabled", False):
            self._check_geometry(node)

        if allowed_types_rule:
            self._check_node_type(node)

        if naming_rule:
            self._check_naming(node)

        self._check_transform_structure(node)

    def _check_frozen_transforms(self, node: SceneNode) -> None:
        if node.mesh_path is None:
            return

        # Gather the transform metadata from the node
        maya_data = node.metadata.get("maya", {})
        translate = maya_data.get("translate", [0, 0, 0])
        rotate = maya_data.get("rotate", [0, 0, 0])
        scale = maya_data.get("scale", [1, 1, 1])

        is_frozen = (
            np.allclose(translate, [0, 0, 0])
            and np.allclose(rotate, [0, 0, 0])
            and np.allclose(scale, [1, 1, 1])
        )

        if not is_frozen:
            severity = self.rules["require_frozen_transforms"]["severity"]
            message = f"Non-frozen transform detected on {node.name}"
            self._report(message, severity, node.name)

    def _check_transform_structure(self, node: SceneNode) -> None:
        """
        Check the structure of transform matrices

        Args:
            node: SceneNode instance to validate
        """
        transform = node.transform

        if transform is None:
            return

        matrix = np.array(transform)

        if matrix.size != 16:
            self._report(
                f"Invalid transform matrix on {node.name}",
                "error",
                node.name,
            )

    def _check_geometry(self, node: SceneNode) -> None:
        """
        Check if nodes have valid geometry

        Args:
            node: SceneNode instance to validate
        """
        if node.mesh_path is None:
            if self.allow_empty_transforms:
                return

            if self.ignore_transform_geometry and node.node_type == "transform":
                return

            severity = self.rules["require_geometry"]["severity"]
            message = f"Missing geometry on node {node.name}"
            self._report(message, severity, node.name)

    def _check_node_type(self, node: SceneNode) -> None:
        """
        Check if node type is allowed

        Args:
            node: SceneNode instance to validate
        """
        allowed = self.rules.get("allowed_node_types")

        if allowed and node.node_type not in allowed:
            message = f"Unsupported node type '{node.node_type}' on {node.name}"
            self._report(message, "error", node.name)

    def _check_unit_scale(self) -> None:
        """
        Check if the unit scale matches the expected value
        """
        expected_unit = self.rules.get("unit_scale")

        if not expected_unit:
            return

        if expected_unit != "cm":
            self.report.warning("Scene unit scale mismatch, expected cm")

    def _check_naming(self, node: SceneNode) -> None:
        """
        Check if node names follow the required naming convention

        Args:
            node: SceneNode instance to validate
        """
        rule = self.rules["enforce_naming_convention"]

        if not rule["enabled"]:
            return

        if not re.match(r"^[A-Za-z0-9_]+$", node.name):
            message = f"Invalid naming convention on node {node.name}"
            self._report(message, rule["severity"], node.name)

    def _check_duplicate_names(self, scene_nodes: list[SceneNode]) -> None:
        """
        Check for duplicate node names

        Args:
            scene_nodes: List of SceneNode instances to validate
        """
        node_seen = set()

        for node in scene_nodes:
            if node.name in node_seen:
                self.report.error(
                    f"Duplicate node name detected: {node.name}",
                    node.name,
                )
            else:
                node_seen.add(node.name)

    def _check_orphan_nodes(self, scene_nodes: list[SceneNode]) -> None:
        """
        Check for orphan nodes that have a parent reference but are not listed as children

        Args:
            scene_nodes: List of SceneNode instances to validate
        """
        for node in scene_nodes:
            if node.parent is None:
                continue

            if node not in node.parent.children:
                self.report.warning(f"Inconsistent hierarchy relationship: {node.name}")

    def _report(self, message: str, severity: str, node_name=None) -> None:
        """
        Record a validation message with the appropriate severity

        Args:
            message (str): The validation message to record
            severity (str): The severity level ("error" or "warning")
            node_name (str | None): Optional name of the node associated with the message
        """
        if severity == "error":
            self.report.error(message, node_name)
        elif severity == "warning":
            self.report.warning(message, node_name)

    def filter_valid_nodes(self, scene_nodes: list[SceneNode]) -> list:
        """
        Remove invalid nodes from SceneGraph

        Args:
            scene_nodes: List of SceneNode instances to filter
        """

        return [
            node for node in scene_nodes if node.name not in self.report.invalid_nodes
        ]

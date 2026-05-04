from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import yaml
import re


class ValidationProfileLoader:
    """Loads YAML validation profiles for pipeline execution."""

    @staticmethod
    def load_file(profile_path: str) -> dict:
        path = Path(profile_path)

        if not path.exists():
            raise FileNotFoundError(f"Validation profile not found: {profile_path}")

        with open(path, "r") as file:
            return yaml.safe_load(file)


@dataclass
class ValidationReport:
    """Stores validation results with severity awareness."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    invalid_nodes: set[str] = field(default_factory=set)

    def error(self, message: str, node_name: str | None = None):
        self.errors.append(message)

        if node_name:
            self.invalid_nodes.add(node_name)

    def warning(self, message: str):
        self.warnings.append(message)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def blocking(self) -> bool:
        return len(self.errors) > 0


class SceneValidator:
    """Executes rule-based validation using YAML profiles."""

    def __init__(self, rules: dict):
        self.rules = rules
        self.report = ValidationReport()

        self.excluded_types = set(rules.get("exclude_node_types", []))

        self.allow_empty_transforms = rules.get("allow_empty_transforms", False)

        self.ignore_transform_geometry = rules.get("require_geometry", {}).get(
            "ignore_transforms_without_shapes", False
        )

    def validate(self, scene_nodes: list):
        self._check_duplicate_names(scene_nodes)
        self._check_orphan_nodes(scene_nodes)
        self._check_unit_scale()

        for node in scene_nodes:
            if node.node_type in self.excluded_types:
                continue

            self._validate_node(node)

        return self.report

    def _validate_node(self, node):
        if self.rules["require_frozen_transforms"]["enabled"]:
            self._check_frozen_transforms(node)

        if self.rules["require_geometry"]["enabled"]:
            self._check_geometry(node)

        if "allowed_node_types" in self.rules:
            self._check_node_type(node)

        if "enforce_naming_convention" in self.rules:
            self._check_naming(node)

        self._check_transform_structure(node)

    def _check_frozen_transforms(self, node):
        transform = node.transform
        if transform is None:
            return

        if (
            self.allow_empty_transforms
            and node.node_type == "transform"
            and node.mesh_path is None
        ):
            return

        identity = np.identity(4)
        if not np.allclose(transform, identity):
            severity = self.rules["require_frozen_transforms"]["severity"]
            message = f"Non-frozen transform detected on {node.name}"
            self._report(message, severity, node.name)

    def _check_transform_structure(self, node):
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

    def _check_geometry(self, node):
        if node.mesh_path is None:
            if self.allow_empty_transforms:
                return

            if self.ignore_transform_geometry and node.node_type == "transform":
                return

            severity = self.rules["require_geometry"]["severity"]
            message = f"Missing geometry on node {node.name}"
            self._report(message, severity, node.name)

    def _check_node_type(self, node):
        allowed = self.rules.get("allowed_node_types")

        if allowed and node.node_type not in allowed:
            message = f"Unsupported node type '{node.node_type}' on {node.name}"
            self._report(message, "error", node.name)

    def _check_unit_scale(self):
        expected_unit = self.rules.get("unit_scale")

        if expected_unit != "cm":
            self.report.warning("Scene unit scale mismatch, expected cm")

    def _check_naming(self, node):
        rule = self.rules["enforce_naming_convention"]

        if not rule["enabled"]:
            return

        if not re.match(r"^[A-Za-z0-9_]+$", node.name):
            message = f"Invalid naming convention on node {node.name}"
            self._report(message, rule["severity"], node.name)

    def _check_duplicate_names(self, scene_nodes):
        node_seen = set()

        for node in scene_nodes:
            if node.name in node_seen:
                self.report.error(
                    f"Duplicate node name detected: {node.name}",
                    node.name,
                )
            else:
                node_seen.add(node.name)

    def _check_orphan_nodes(self, scene_nodes):
        for node in scene_nodes:
            if node.parent is None:
                continue

            if node not in node.parent.children:
                self.report.warning(f"Inconsistent hierarchy relationship: {node.name}")

    def _report(self, message: str, severity: str, node_name=None):
        if severity == "error":
            self.report.error(message, node_name)
        elif severity == "warning":
            self.report.warning(message)

    def filter_valid_nodes(self, scene_nodes):
        """
        Remove invalid nodes from SceneGraph
        """

        return [
            node for node in scene_nodes if node.name not in self.report.invalid_nodes
        ]

import json
import socket
import hashlib
from datetime import datetime
from pathlib import Path


class MetadataWriter:
    @staticmethod
    def _profile_hash(profile_path: str) -> str:
        """
        Calculate a hash of the validation profile

        Args:
            profile_path (str): Path to the validation profile file
        """
        with open(str(profile_path), "rb") as file:
            return hashlib.sha1(file.read()).hexdigest()

    @staticmethod
    def _count_nodes(exported_nodes: int | list | None) -> int:
        """
        Count the number of exported nodes

        Args:
            exported_nodes: Can be an int, a list of nodes, or any iterable of nodes
        """
        if exported_nodes is None:
            return 0

        if isinstance(exported_nodes, int):
            return exported_nodes

        try:
            return len(exported_nodes)
        except TypeError:
            return 1

    @staticmethod
    def write(
        output_path: str,
        publish_id: str,
        scene_name: str,
        source_dcc: str,
        target_dcc: str,
        validation_profile: str,
        validation_profile_hash: str,
        validation_status: str,
        report: object,
        exported_nodes: int | list | None,
        node_uuids: list[str] | None = None,
    ) -> str:
        """
        Write metadata to a JSON file alongside the exported data

        Args:
            output_path (str): Path to the exported data file
            publish_id (str): Unique identifier for the publish
            scene_name (str): Name of the source scene
            source_dcc (str): Name of the source DCC application
            target_dcc (str): Name of the target DCC application
            validation_profile (str): Name of the validation profile used
            validation_profile_hash (str): Hash of the validation profile
            validation_status (str): Result of the validation (e.g., "passed", "failed")
            report: Validation report containing errors and warnings
            exported_nodes: Number of nodes exported or a list of exported nodes
            node_uuids: Optional list of UUIDs for the exported nodes
        """
        node_count = MetadataWriter._count_nodes(exported_nodes)

        metadata = {
            "publish_id": publish_id,
            "scene": scene_name,
            "source_dcc": source_dcc,
            "target_dcc": target_dcc,
            "validation_profile": validation_profile,
            "validation_profile_hash": validation_profile_hash,
            "validation_status": validation_status,
            "errors": report.errors,
            "warnings": report.warnings,
            "exported_nodes": node_count,
            "output_path": str(output_path),
            "machine": socket.gethostname(),
            "timestamp": datetime.now().isoformat(),
        }

        if node_uuids:
            metadata["node_uuids"] = node_uuids

        metadata_path = Path(output_path).with_suffix(".metadata.json")

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

        return metadata_path

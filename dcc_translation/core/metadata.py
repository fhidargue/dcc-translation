import json
import socket
import hashlib
from datetime import datetime
from pathlib import Path


class MetadataWriter:
    @staticmethod
    def _profile_hash(profile_path: str) -> str:
        with open(str(profile_path), "rb") as file:
            return hashlib.sha1(file.read()).hexdigest()

    @staticmethod
    def _count_nodes(exported_nodes):
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
        report,
        exported_nodes,
        node_uuids=None,
    ):
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

from datetime import datetime

from dcc_translation.core.validator import (
    SceneValidator,
    ValidationProfileLoader,
)
from dcc_translation.exporter.usd_exporter import USDExporter
from dcc_translation.database.translation_registry import TranslationRegistry
from dcc_translation.core.metadata import MetadataWriter

import uuid


def run_translation_pipeline(
    adapter,
    profile_path,
    output_path,
    backend="sqlite",
    db_path=None,
):
    if backend == "sqlite" and db_path is None:
        raise ValueError("SQLite backend requires explicit db_path")

    publish_id = str(uuid.uuid4())

    # Compute profile hash
    profile_hash = MetadataWriter._profile_hash(profile_path)

    # Extract all the valid nodes from the Maya scene
    rules = ValidationProfileLoader.load_file(profile_path)
    scene_nodes = adapter.extract_scene_nodes(rules)

    # Validate the rules from the YAML file
    validator = SceneValidator(rules)
    report = validator.validate(scene_nodes)
    validation_status = "failed" if report.blocking else "success"

    # Filter to only valid nodes based on YAML file
    filtered_nodes = validator.filter_valid_nodes(scene_nodes)

    for node in filtered_nodes:
        node.publish_id = publish_id

    # Export the Maya scene into a USD file
    exporter = USDExporter(output_path)
    exporter.export(filtered_nodes)

    # Define metadata variables
    scene_name = adapter.get_scene_name()
    source_dcc = adapter.get_source_dcc_name()
    target_dcc = rules.get("pipeline_target", "unknown")

    MetadataWriter.write(
        output_path=output_path,
        publish_id=publish_id,
        scene_name=scene_name,
        source_dcc=source_dcc,
        target_dcc=target_dcc,
        validation_profile=profile_path,
        validation_profile_hash=profile_hash,
        validation_status=validation_status,
        report=report,
        exported_nodes=len(filtered_nodes),
    )

    # Registry logging
    registry = TranslationRegistry(
        backend=backend,
        db_path=db_path if backend == "sqlite" else None,
    )

    registry.store_translation(
        publish_id=publish_id,
        scene=scene_name,
        source_dcc=source_dcc,
        target_dcc=target_dcc,
        export_format="usd",
        validation_profile=profile_path,
        validation_profile_hash=profile_hash,
        validation_status=validation_status,
        import_status="pending",
        output_path=output_path,
        exported_nodes=len(filtered_nodes),
        error_count=len(report.errors),
        warning_count=len(report.warnings),
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )

    # Handle node dependencies
    dependency_records = []

    for node in filtered_nodes:
        for dep in getattr(node, "dependencies", []):
            dependency_records.append(
                {
                    "publish_id": publish_id,
                    "node_uuid": node.uuid,
                    "dependency": dep,
                }
            )

    registry.backend.store_dependencies(dependency_records)

    registry.backend.store_validation_report(
        {
            "publish_id": publish_id,
            "errors": report.errors,
            "warnings": report.warnings,
        }
    )

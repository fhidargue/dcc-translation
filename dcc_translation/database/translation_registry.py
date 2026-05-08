from .backend.sqlite_backend import SQLiteBackend
from .backend.mongo_backend import MongoBackend
from pathlib import Path


class TranslationRegistry:
    """
    Tracks publish pipeline execution metadata using a configurable backend
    """

    def __init__(self, backend="sqlite", db_path=None):
        self.backend_name = backend

        if backend == "mongo":
            self.backend = MongoBackend()
            self.connection = None
            self.db_path = None
        elif backend == "sqlite":
            if db_path is None:
                raise ValueError("SQLite backend requires db_path")

            self.db_path = Path(db_path)
            self.backend = SQLiteBackend(self.db_path)
            self.connection = self.backend.connection
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def store_translation(
        self,
        publish_id: str,
        scene: str,
        source_dcc: str,
        target_dcc: str,
        export_format: str,
        validation_profile: str,
        validation_profile_hash: str,
        validation_status: str,
        import_status: str,
        output_path: str,
        exported_nodes: int,
        error_count: int,
        warning_count: int,
        timestamp: str,
    ) -> None:
        """
        Store a translation publish record in the registry

        Args:
            publish_id (str): Unique identifier for the publish
            scene (str): Scene name or path
            source_dcc (str): Source DCC application
            target_dcc (str): Target DCC application
            export_format (str): Export format used
            validation_profile (str): Validation profile name
            validation_profile_hash (str): Hash of the validation profile
            validation_status (str): Validation status (e.g. "passed", "failed")
            import_status (str): Import status in target DCC (e.g. "pending", "completed", "failed")
            output_path (str): Path to the exported file
            exported_nodes (int): Number of exported nodes or assets
            error_count (int): Number of errors during export/validation/import
            warning_count (int): Number of warnings during export/validation/import
            timestamp (str): Timestamp of the translation process
        """
        self.backend.store_translation(
            publish_id=publish_id,
            scene=scene,
            source_dcc=source_dcc,
            target_dcc=target_dcc,
            export_format=export_format,
            validation_profile=validation_profile,
            validation_profile_hash=validation_profile_hash,
            validation_status=validation_status,
            import_status=import_status,
            output_path=output_path,
            exported_nodes=exported_nodes,
            error_count=error_count,
            warning_count=warning_count,
            timestamp=timestamp,
        )

    def fetch_translations(self) -> list[dict]:
        """
        Fetch all translation records from the registry
        """

        return self.backend.fetch_translations()

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
        publish_id,
        scene,
        source_dcc,
        target_dcc,
        export_format,
        validation_profile,
        validation_profile_hash,
        validation_status,
        import_status,
        output_path,
        exported_nodes,
        error_count,
        warning_count,
        timestamp,
    ):
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

    def fetch_translations(self):
        return self.backend.fetch_translations()

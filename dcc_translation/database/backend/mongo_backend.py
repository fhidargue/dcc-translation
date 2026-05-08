import datetime

from pymongo import MongoClient

from .registry_backend import RegistryBackend
from dcc_translation.database.mongo_setup import MongoSetup
from dcc_translation.config.env import mongo_pipeline_uri, MONGO_DB


class MongoBackend(RegistryBackend):
    def __init__(self, uri: str | None = None):
        MongoSetup().bootstrap()

        self.client = MongoClient(mongo_pipeline_uri())
        self.db = self.client[MONGO_DB]

        # Collections
        self.collection = self.db["translations"]
        self.dependencies = self.db["dependencies"]
        self.validation_reports = self.db["validation_reports"]

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
        exported_nodes: list,
        error_count: int,
        warning_count: int,
        timestamp: datetime.datetime,
    ) -> None:
        """
        Insert translation publish record

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
            exported_nodes (list): List of exported nodes or assets
            error_count (int): Number of errors during export/validation/import
            warning_count (int): Number of warnings during export/validation/import
            timestamp (datetime): Timestamp of the translation process
        """

        document = {
            "publish_id": publish_id,
            "scene": scene,
            "source_dcc": source_dcc,
            "target_dcc": target_dcc,
            "export_format": export_format,
            "validation_profile": validation_profile,
            "validation_profile_hash": validation_profile_hash,
            "validation_status": validation_status,
            "import_status": import_status,
            "output_path": output_path,
            "exported_nodes": exported_nodes,
            "error_count": error_count,
            "warning_count": warning_count,
            "timestamp": timestamp,
        }

        self.collection.insert_one(document)

    def fetch_translations(self) -> list[dict]:
        """
        Return all translation records
        """

        return list(self.collection.find({}, {"_id": 0}))

    def store_dependencies(self, records: list[dict]) -> None:
        """
        Create dependency records for a publish

        Args:
            records (list of dict): List of dependency records
        """
        if records:
            self.dependencies.insert_many(records)

    def fetch_dependencies(self, publish_id: str) -> list[dict]:
        """
        Fetch dependency records for a specific publish

        Args:
            publish_id (str): Unique identifier for the publish
        """
        return list(
            self.dependencies.find(
                {"publish_id": publish_id},
                {"_id": 0},
            )
        )

    def store_validation_report(self, report_data: dict) -> None:
        """
        Create a validation report record for a publish

        Args:
            report_data (dict): Validation report data containing at least "publish_id" and other relevant fields
        """
        self.validation_reports.insert_one(report_data)

    def fetch_validation_report(self, publish_id: str) -> dict | None:
        """
        Fetch a validation report record for a publish

        Args:
            publish_id (str): Unique identifier for the publish
        """
        return self.validation_reports.find_one(
            {"publish_id": publish_id},
            {"_id": 0},
        )

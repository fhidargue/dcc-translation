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
        """
        Insert translation publish record
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

    def fetch_translations(self):
        """
        Return all translation records
        """

        return list(self.collection.find({}, {"_id": 0}))

    def store_dependencies(self, records):
        if records:
            self.dependencies.insert_many(records)

    def fetch_dependencies(self, publish_id):
        return list(
            self.dependencies.find(
                {"publish_id": publish_id},
                {"_id": 0},
            )
        )

    def store_validation_report(self, report_data):
        self.validation_reports.insert_one(report_data)

    def fetch_validation_report(self, publish_id):
        return self.validation_reports.find_one(
            {"publish_id": publish_id},
            {"_id": 0},
        )

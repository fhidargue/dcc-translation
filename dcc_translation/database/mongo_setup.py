from pymongo import MongoClient
from pymongo.errors import OperationFailure
from dcc_translation.config.env import mongo_admin_uri, MONGO_DB


class MongoSetup:
    """
    Creates database structure, users, roles and indexes programmatically
    """

    def __init__(self, db_name=MONGO_DB):
        self.client = MongoClient(mongo_admin_uri())
        self.client.admin.command("ping")

        self.admin_db = self.client["admin"]
        self.db = self.client[db_name]
        self.db_name = db_name

    def create_pipeline_user(self):
        try:
            users = self.client.admin.command("usersInfo")

            existing_users = [user["user"] for user in users.get("users", [])]

            if "pipeline_user" in existing_users:
                return

            self.db.command(
                "createUser",
                "pipeline_user",
                pwd="pipeline_pass",
                roles=[{"role": "readWrite", "db": self.db_name}],
            )
        except OperationFailure as e:
            if "already exists" not in str(e):
                raise

    def create_collections(self):
        required = {
            "translations",
            "dependencies",
            "validation_reports",
        }

        existing = set(self.db.list_collection_names())

        for name in required - existing:
            self.db.create_collection(name)

    def create_indexes(self):
        translations = self.db["translations"]
        dependencies = self.db["dependencies"]
        validation_reports = self.db["validation_reports"]

        translations.create_index("publish_id", unique=True)
        translations.create_index("timestamp")
        translations.create_index("scene")

        dependencies.create_index("publish_id")
        dependencies.create_index("node_uuid")

        validation_reports.create_index("publish_id")

    def bootstrap(self):
        self.create_pipeline_user()
        self.create_collections()
        self.create_indexes()

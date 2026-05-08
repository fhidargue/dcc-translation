from .registry_backend import RegistryBackend
import sqlite3
import json


class SQLiteBackend(RegistryBackend):
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self) -> None:
        """
        Create necessary tables if they don't exist
        """
        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS translations (
                publish_id TEXT,
                scene TEXT,
                source_dcc TEXT,
                target_dcc TEXT,
                export_format TEXT,
                validation_profile TEXT,
                validation_profile_hash TEXT,
                validation_status TEXT,
                import_status TEXT,
                output_path TEXT,
                exported_nodes INTEGER,
                error_count INTEGER,
                warning_count INTEGER,
                timestamp TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dependencies (
                publish_id TEXT,
                node_uuid TEXT,
                dependency TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS validation_reports (
                publish_id TEXT,
                errors TEXT,
                warnings TEXT
            )
            """
        )

        self.connection.commit()

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
        Create a translation record

        Args:
            publish_id (str): Unique identifier for the publish
            scene (str): Scene name or identifier
            source_dcc (str): Source DCC application
            target_dcc (str): Target DCC application
            export_format (str): Format used for export
            validation_profile (str): Validation profile name or identifier
            validation_profile_hash (str): Hash of the validation profile used
            validation_status (str): Status of the validation step (e.g., "passed", "failed")
            import_status (str): Status of the import step (e.g., "pending", "completed", "failed")
            output_path (str): File path where the translated output is stored
            exported_nodes (int): Number of nodes exported during translation
            error_count (int): Number of errors encountered during translation
            warning_count (int): Number of warnings encountered during translation
            timestamp (str): Timestamp of when the translation was performed
        """
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO translations
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
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
            ),
        )

        self.connection.commit()

    def fetch_translations(self) -> list[dict]:
        """
        Return all translation records as dictionaries
        """

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM translations")

        columns = [col[0] for col in cursor.description]

        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def store_dependencies(self, records: list[dict]) -> None:
        """
        Store dependency records for a publish
        """

        if not records:
            return

        cursor = self.connection.cursor()

        cursor.executemany(
            """
            INSERT INTO dependencies
            VALUES (?, ?, ?)
            """,
            [
                (
                    record["publish_id"],
                    record["node_uuid"],
                    record["dependency"],
                )
                for record in records
            ],
        )

        self.connection.commit()

    def fetch_dependencies(self, publish_id: str) -> list[dict]:
        """
        Return dependencies associated with a publish_id
        """

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT node_uuid, dependency
            FROM dependencies
            WHERE publish_id = ?
            """,
            (publish_id,),
        )

        return [
            {
                "node_uuid": row[0],
                "dependency": row[1],
            }
            for row in cursor.fetchall()
        ]

    def store_validation_report(self, report_data: dict) -> None:
        """
        Create a validation report record for a publish

        Args:
            report_data (dict): Validation report data containing at least "publish_id" and other relevant fields
        """
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO validation_reports
            VALUES (?, ?, ?)
            """,
            (
                report_data["publish_id"],
                json.dumps(report_data["errors"]),
                json.dumps(report_data["warnings"]),
            ),
        )

        self.connection.commit()

    def fetch_validation_report(self, publish_id: str) -> dict | None:
        """
        Fetch a validation report record for a publish

        Args:
            publish_id (str): Unique identifier for the publish
        """
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT errors, warnings
            FROM validation_reports
            WHERE publish_id = ?
            """,
            (publish_id,),
        )

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "errors": json.loads(row[0]),
            "warnings": json.loads(row[1]),
        }

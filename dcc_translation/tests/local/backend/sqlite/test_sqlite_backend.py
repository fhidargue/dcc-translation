import uuid
import pytest
from datetime import datetime

from dcc_translation.database.backend.sqlite_backend import SQLiteBackend

pytestmark = pytest.mark.local


def test_sqlite_backend_insert(tmp_path):

    db_path = tmp_path / "translations.db"

    backend = SQLiteBackend(str(db_path))

    backend.store_translation(
        publish_id=str(uuid.uuid4()),
        scene="scene",
        source_dcc="maya",
        target_dcc="unreal",
        export_format="usd",
        validation_profile="profile.yml",
        validation_profile_hash="hash",
        validation_status="success",
        import_status="pending",
        output_path="scene.usda",
        exported_nodes=1,
        error_count=0,
        warning_count=0,
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )

    cursor = backend.connection.cursor()
    cursor.execute("SELECT * FROM translations")

    results = cursor.fetchall()

    assert len(results) == 1

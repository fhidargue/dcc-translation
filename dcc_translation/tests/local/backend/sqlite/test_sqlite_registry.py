import uuid
import pytest

from dcc_translation.database.translation_registry import TranslationRegistry
from dcc_translation.core.pipeline import run_translation_pipeline
from dcc_translation.adapters.mock_adapter import MockAdapter
from datetime import datetime

pytestmark = pytest.mark.local


DB_PATH = "translations.db"


def test_registry_creation(tmp_path):
    db_path = tmp_path / DB_PATH

    registry = TranslationRegistry(db_path=str(db_path))

    assert db_path.exists()
    assert registry.db_path == db_path


def test_translation_insert(tmp_path):
    db_path = tmp_path / DB_PATH

    registry = TranslationRegistry(db_path=str(db_path))
    registry.store_translation(
        publish_id=str(uuid.uuid4()),
        scene="testing_scene",
        source_dcc="maya",
        target_dcc="unreal",
        export_format="usd",
        validation_profile="maya_to_unreal.yml",
        validation_profile_hash="abc123hash",
        validation_status="success",
        import_status="success",
        output_path="scene.usda",
        exported_nodes=1,
        error_count=0,
        warning_count=0,
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )

    cursor = registry.connection.cursor()
    cursor.execute("SELECT * FROM translations")
    results = cursor.fetchall()

    assert len(results) == 1


def test_pipeline_logs_publish(tmp_path):
    db_path = tmp_path / DB_PATH
    usd_path = tmp_path / "scene.usda"
    adapter = MockAdapter()

    run_translation_pipeline(
        adapter=adapter,
        profile_path="dcc_translation/validation_profiles/maya_to_unreal.yml",
        output_path=str(usd_path),
        db_path=str(db_path),
    )

    registry = TranslationRegistry(db_path=str(db_path))
    cursor = registry.connection.cursor()
    cursor.execute("SELECT * FROM translations")
    results = cursor.fetchall()

    assert len(results) >= 1


def test_store_dependencies(tmp_path):
    db_path = tmp_path / "translations.db"

    registry = TranslationRegistry(
        backend="sqlite",
        db_path=str(db_path),
    )

    publish_id = str(uuid.uuid4())

    registry.backend.store_dependencies(
        [
            {
                "publish_id": publish_id,
                "node_uuid": "nodeA",
                "dependency": "textureA.exr",
            },
            {
                "publish_id": publish_id,
                "node_uuid": "nodeB",
                "dependency": "materialB.usd",
            },
        ]
    )

    deps = registry.backend.fetch_dependencies(publish_id)

    assert len(deps) == 2
    assert deps[0]["dependency"] in {"textureA.exr", "materialB.usd"}


def test_validation_report_storage(tmp_path):
    db_path = tmp_path / "translations.db"

    registry = TranslationRegistry(
        backend="sqlite",
        db_path=str(db_path),
    )

    publish_id = str(uuid.uuid4())

    registry.backend.store_validation_report(
        {
            "publish_id": publish_id,
            "errors": ["bad transform"],
            "warnings": ["naming issue"],
        }
    )

    report = registry.backend.fetch_validation_report(publish_id)

    assert report["errors"] == ["bad transform"]
    assert report["warnings"] == ["naming issue"]

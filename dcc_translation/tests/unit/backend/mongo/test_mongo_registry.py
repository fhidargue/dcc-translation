import uuid
from datetime import datetime

import pytest
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

from dcc_translation.database.mongo_setup import MongoSetup
from dcc_translation.database.translation_registry import TranslationRegistry
from dcc_translation.adapters.mock_adapter import MockAdapter
from dcc_translation.core.pipeline import run_translation_pipeline
from dcc_translation.config.env import mongo_pipeline_uri

pytestmark = pytest.mark.local


EXPECTED_SCHEMA = {
    "publish_id",
    "scene",
    "source_dcc",
    "target_dcc",
    "export_format",
    "validation_profile",
    "validation_profile_hash",
    "validation_status",
    "import_status",
    "output_path",
    "exported_nodes",
    "error_count",
    "warning_count",
    "timestamp",
}


@pytest.fixture(scope="session", autouse=True)
def ensure_mongo_bootstrap():
    try:
        MongoSetup().bootstrap()
    except (ServerSelectionTimeoutError, OperationFailure):
        pytest.skip("MongoDB container not running")


@pytest.fixture(scope="function")
def registry():
    return TranslationRegistry(backend="mongo")


@pytest.fixture(scope="function")
def sample_record():
    return dict(
        publish_id=str(uuid.uuid4()),
        scene="mongo_scene",
        source_dcc="maya",
        target_dcc="unreal",
        export_format="usd",
        validation_profile="maya_to_unreal.yml",
        validation_profile_hash="hash123",
        validation_status="success",
        import_status="pending",
        output_path="scene.usda",
        exported_nodes=2,
        error_count=0,
        warning_count=1,
        timestamp=datetime.now().isoformat(timespec="seconds"),
    )


def test_registry_insert(registry, sample_record):
    registry.store_translation(**sample_record)
    results = registry.fetch_translations()

    assert any(r["publish_id"] == sample_record["publish_id"] for r in results)


def test_publish_id_uniqueness(registry, sample_record):
    registry.store_translation(**sample_record)
    with pytest.raises(Exception):
        registry.store_translation(**sample_record)


def test_schema_matches_sqlite(registry):
    results = registry.fetch_translations()

    if results:
        assert EXPECTED_SCHEMA.issubset(results[0].keys())


def test_pipeline_logs_publish(tmp_path, registry):
    adapter = MockAdapter()

    run_translation_pipeline(
        adapter=adapter,
        profile_path="dcc_translation/validation_profiles/maya_to_unreal.yml",
        output_path=str(tmp_path / "scene.usda"),
        backend="mongo",
    )

    results = registry.fetch_translations()

    assert len(results) >= 1


def test_indexes_exist():
    client = MongoClient(mongo_pipeline_uri())
    indexes = client["dcc_translation"]["translations"].index_information()

    assert {"publish_id_1", "timestamp_1", "scene_1"}.issubset(indexes.keys())


def test_store_dependencies(registry):
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


def test_validation_report_storage(registry):
    publish_id = str(uuid.uuid4())

    registry.backend.store_validation_report(
        {
            "publish_id": publish_id,
            "errors": ["missing mesh"],
            "warnings": ["naming issue"],
        }
    )

    report = registry.backend.fetch_validation_report(publish_id)

    assert report["errors"] == ["missing mesh"]
    assert report["warnings"] == ["naming issue"]

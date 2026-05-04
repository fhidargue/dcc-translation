from dcc_translation.adapters.mock_adapter import MockAdapter
from dcc_translation.core.pipeline import run_translation_pipeline
from dcc_translation.database.translation_registry import TranslationRegistry

import pytest


pytestmark = pytest.mark.local


def test_pipeline_logs_validation_report(tmp_path):
    adapter = MockAdapter()

    db_path = tmp_path / "translations.db"

    run_translation_pipeline(
        adapter=adapter,
        profile_path="dcc_translation/validation_profiles/maya_to_unreal.yml",
        output_path=str(tmp_path / "scene.usda"),
        backend="sqlite",
        db_path=str(db_path),
    )

    registry = TranslationRegistry(
        backend="sqlite",
        db_path=str(db_path),
    )

    publish_id = registry.fetch_translations()[0]["publish_id"]

    report = registry.backend.fetch_validation_report(publish_id)

    assert report is not None

from dcc_translation.core.pipeline import run_translation_pipeline
from dcc_translation.adapters.mock_adapter import MockAdapter

import pytest

pytestmark = pytest.mark.local


def test_metadata_written(tmp_path):
    usd_path = tmp_path / "scene.usda"
    db_path = tmp_path / "translations.db"
    adapter = MockAdapter()

    run_translation_pipeline(
        adapter=adapter,
        profile_path="dcc_translation/validation_profiles/maya_to_unreal.yml",
        output_path=str(usd_path),
        db_path=str(db_path),
    )

    metadata_file = usd_path.with_suffix(".metadata.json")

    assert metadata_file.exists()

    contents = metadata_file.read_text()

    assert "validation_status" in contents
    assert "exported_nodes" in contents

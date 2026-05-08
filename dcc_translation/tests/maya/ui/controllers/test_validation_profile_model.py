import pytest
import yaml

from pathlib import Path

from dcc_translation.ui.validation_profile_model import ValidationProfileModel

pytestmark = pytest.mark.maya


def test_load_profile(
    tmp_path,
):
    """
    Load YAML profile successfully
    """

    profile_path = tmp_path / "profile.yml"
    profile_data = {
        "unit_scale": "cm",
        "require_geometry": {
            "enabled": True,
        },
    }

    with open(profile_path, "w") as file:
        yaml.safe_dump(
            profile_data,
            file,
        )

    model = ValidationProfileModel(str(profile_path))
    data = model.load()

    assert data["unit_scale"] == "cm"
    assert data["require_geometry"]["enabled"] is True


def test_save_profile(
    tmp_path,
):
    """
    Save YAML profile successfully
    """

    profile_path = tmp_path / "profile.yml"
    model = ValidationProfileModel(str(profile_path))
    model.data = {
        "allowed_node_types": [
            "mesh",
            "transform",
        ],
    }

    model.save()

    assert profile_path.exists()

    with open(profile_path, "r") as file:
        data = yaml.safe_load(file)

    assert data["allowed_node_types"] == [
        "mesh",
        "transform",
    ]


def test_load_missing_profile(
    tmp_path,
):
    """
    Missing YAML file returns empty dictionary
    """

    profile_path = tmp_path / "missing.yml"
    model = ValidationProfileModel(str(profile_path))
    data = model.load()

    assert data == {}


def test_load_invalid_yaml(
    tmp_path,
):
    """
    Invalid YAML raises exception
    """

    profile_path = tmp_path / "invalid.yml"

    with open(profile_path, "w") as file:
        file.write("invalid: [unclosed")

    model = ValidationProfileModel(str(profile_path))

    with pytest.raises(Exception):
        model.load()


def test_save_overwrites_existing_profile(
    tmp_path,
):
    """
    Saving profile overwrites previous content
    """

    profile_path = tmp_path / "profile.yml"

    with open(profile_path, "w") as file:
        yaml.safe_dump(
            {
                "unit_scale": "m",
            },
            file,
        )

    model = ValidationProfileModel(str(profile_path))
    model.data = {
        "unit_scale": "cm",
    }
    model.save()

    with open(profile_path, "r") as file:
        data = yaml.safe_load(file)

    assert data["unit_scale"] == "cm"


def test_profile_persistence(
    tmp_path,
):
    """
    Saved profile can be reloaded correctly
    """

    profile_path = tmp_path / "profile.yml"
    model = ValidationProfileModel(str(profile_path))
    original_data = {
        "require_geometry": {
            "enabled": True,
            "severity": "error",
        },
    }

    model.data = original_data
    model.save()
    loaded_data = model.load()

    assert loaded_data == original_data


def test_empty_profile_file(
    tmp_path,
):
    """
    Empty YAML file loads as empty dictionary
    """

    profile_path = tmp_path / "empty.yml"
    profile_path.write_text("")
    model = ValidationProfileModel(str(profile_path))
    data = model.load()

    assert data == {}


def test_nested_profile_data(
    tmp_path,
):
    """
    Nested YAML structures load correctly
    """

    profile_path = tmp_path / "nested.yml"

    nested_data = {
        "validation": {
            "geometry": {
                "enabled": True,
                "severity": "warning",
            },
        },
    }

    with open(profile_path, "w") as file:
        yaml.safe_dump(
            nested_data,
            file,
        )

    model = ValidationProfileModel(str(profile_path))
    data = model.load()

    assert data["validation"]["geometry"]["enabled"] is True

    assert data["validation"]["geometry"]["severity"] == "warning"


def test_path_stored_correctly(
    tmp_path,
):
    """
    Model stores profile path
    """

    profile_path = tmp_path / "profile.yml"
    model = ValidationProfileModel(str(profile_path))

    assert Path(model.profile_path) == profile_path


def test_save_creates_file(
    tmp_path,
):
    """
    Save creates YAML file if missing
    """

    profile_path = tmp_path / "new_profile.yml"
    model = ValidationProfileModel(str(profile_path))
    model.data = {
        "pipeline_target": "unreal",
    }
    model.save()

    assert profile_path.exists()


def test_load_preserves_list_values(
    tmp_path,
):
    """
    YAML lists load correctly
    """

    profile_path = tmp_path / "lists.yml"
    profile_data = {
        "allowed_node_types": [
            "mesh",
            "transform",
            "camera",
        ],
    }

    with open(profile_path, "w") as file:
        yaml.safe_dump(
            profile_data,
            file,
        )

    model = ValidationProfileModel(str(profile_path))
    data = model.load()

    assert len(data["allowed_node_types"]) == 3
    assert "camera" in data["allowed_node_types"]

from dcc_translation.adapters.maya_adapter import MayaAdapter
from dcc_translation.core.validator import SceneValidator


def validate_scene(profile_data: dict) -> dict:
    """
    Run scene validation

    Args:
        profile_data (dict): Validation rules and thresholds loaded from profile
    """

    profile_data = profile_data or {}

    adapter = MayaAdapter()
    validator = SceneValidator(profile_data)
    scene_nodes = adapter.extract_scene_nodes(profile_data)
    report = validator.validate(scene_nodes)

    return report

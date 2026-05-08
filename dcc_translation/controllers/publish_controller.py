from pathlib import Path

from dcc_translation.adapters.maya_adapter import MayaAdapter
from dcc_translation.core.pipeline import run_translation_pipeline
from dcc_translation.cli.cli import resolve_profile
from dcc_translation.utils.backend_detection import select_registry_backend


def publish_scene(
    output_path: str,
    target: str = "unreal",
) -> dict:
    """
    Run full publish pipeline

    Args:
        output_path (str): Path to output USD file
        target (str): Target DCC for validation profile (e.g. "unreal")
    """

    profile_path = resolve_profile(target)

    backend = select_registry_backend()

    adapter = MayaAdapter()

    run_translation_pipeline(
        adapter=adapter,
        profile_path=profile_path,
        output_path=output_path,
        backend=backend,
        db_path=(
            str(Path(output_path).with_suffix(".db")) if backend == "sqlite" else None
        ),
    )

    return {
        "output_path": output_path,
        "backend": backend,
        "profile_path": profile_path,
    }

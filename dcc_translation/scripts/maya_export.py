import sys
import importlib
from pathlib import Path

import dcc_translation

from dcc_translation.adapters.maya_adapter import MayaAdapter
from dcc_translation.core.pipeline import run_translation_pipeline
from dcc_translation.utils.backend_detection import select_registry_backend
from dcc_translation.utils.maya_logging import info, warning, error


def publish_usd(output_path: str, target: str = "unreal") -> str:
    """
    Maya publish scene into USDA file

    Runs:
        Scene extraction
        Validation
        USD export
        Metadata write
        Registry logging
        Backend detection (Mongo or SQLite fallback)

    Args:
        output_path (str): The file path where the USDA file will be saved
        target (str): The target DCC or engine for validation profile selection (default: "unreal")
    """

    info("Reloading pipeline modules")

    try:
        for module in list(sys.modules):
            if module.startswith("dcc_translation"):
                importlib.reload(sys.modules[module])

        info("- Reloaded pipeline modules")

    except Exception as e:
        warning(f"Module reload skipped: {e}")

    try:
        info("Resolving validation profile")

        profile_path = (
            Path(dcc_translation.__file__).parent
            / "validation_profiles"
            / f"maya_to_{target}.yml"
        )

        if not profile_path.exists():
            raise FileNotFoundError(f"Validation profile not found: {profile_path}")

        info(f"- Using profile: {profile_path.name}")
    except Exception as e:
        error(f"Profile resolution failed: {e}")
        raise

    try:
        info("Detecting registry backend")

        backend = select_registry_backend()

        info(f"- Detected backend: {backend}")

    except Exception as e:
        warning(f"Backend detection failed: {e}")
        backend = "sqlite"

    try:
        info("Running translation pipeline")

        adapter = MayaAdapter()

        run_translation_pipeline(
            adapter=adapter,
            profile_path=str(profile_path),
            output_path=str(output_path),
            backend=backend,
            db_path=(
                str(Path(output_path).with_suffix(".db"))
                if backend == "sqlite"
                else None
            ),
        )

        info(f"- Export completed: {output_path}")
    except Exception as e:
        error(f"Publish failed: {e}")
        raise

    info("Publish complete")

    return output_path

#!/usr/bin/env -S uv run --script

from pathlib import Path
from dcc_translation.core.pipeline import run_translation_pipeline


def main():
    profile_path = "src/dcc_translation/validation_profiles/maya_to_unreal.yml"
    output_path = Path("scene.usda")
    db_path = Path("translations.db")

    run_translation_pipeline(
        profile_path=str(profile_path),
        output_path=str(output_path),
        db_path=str(db_path),
    )

    print(f"USD file written to: {output_path.resolve()}")
    print(f"Registry updated at: {db_path.resolve()}")


if __name__ == "__main__":
    main()

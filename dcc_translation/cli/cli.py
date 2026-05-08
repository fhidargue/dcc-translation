import argparse
import dcc_translation
from pathlib import Path

from dcc_translation.core.pipeline import run_translation_pipeline
from dcc_translation.core.validator import (
    SceneValidator,
    ValidationProfileLoader,
)
from dcc_translation.database.translation_registry import TranslationRegistry
from dcc_translation.utils.backend_detection import select_registry_backend
from dcc_translation.utils.maya_logging import info


# Helper functions
def resolve_adapter(dcc: str, command: str) -> object:
    """
    Resolve adapter implementation from CLI argument

    Args:
        dcc (str): DCC name (e.g. "maya", "mock")
        command (str): Command being executed (e.g. "publish", "validate", "inspect")
    """

    if dcc == "maya":
        from dcc_translation.adapters.maya_adapter import MayaAdapter

        adapter = MayaAdapter()
        extra_arg = " --out usd_file.usda" if command == "publish" else ""

        if getattr(adapter, "cmds", None) is None:
            raise RuntimeError(
                "Maya adapter requires the Maya environment.\n"
                "Run inside the Maya Script Editor or use:\n"
                f"* dcc-translate {command} --dcc mock --target unreal{extra_arg}"
            )
        return adapter

    if dcc == "mock":
        from dcc_translation.adapters.mock_adapter import MockAdapter

        return MockAdapter()

    raise ValueError(f"Unsupported DCC adapter: {dcc}")


def resolve_profile(target: str) -> str:
    """
    Resolve validation profile path from target name

    Args:
        target (str): Target DCC (e.g. "unreal", "houdini")
    """

    package_root = Path(dcc_translation.__file__).parent
    profile_path = package_root / "validation_profiles" / f"maya_to_{target}.yml"

    if not profile_path.exists():
        raise FileNotFoundError(f"No validation profile found for target '{target}'")

    return str(profile_path)


def print_registry_table(rows: list[dict]) -> None:
    """
    Pretty-print registry rows

    Args:
        rows (list of dict): Registry records to print
    """

    print(f"\nPublish history ({len(rows)} records):\n")

    headers = (
        "PublishID",
        "Scene",
        "Source",
        "Target",
        "Format",
        "Validation",
        "Profile",
        "Hash",
        "Nodes",
        "Errors",
        "Warnings",
        "Import",
        "Output",
        "Timestamp",
    )

    row_format = (
        "{:<36} "
        "{:<15} "
        "{:<8} "
        "{:<8} "
        "{:<7} "
        "{:<10} "
        "{:<22} "
        "{:<12} "
        "{:<6} "
        "{:<6} "
        "{:<8} "
        "{:<10} "
        "{:<15} "
        "{}"
    )

    print(row_format.format(*headers))
    print("-" * 200)

    for row in rows:
        print(
            row_format.format(
                row["publish_id"],
                row["scene"],
                row["source_dcc"],
                row["target_dcc"],
                row["export_format"],
                row["validation_status"],
                Path(row["validation_profile"]).name[:22],
                row["validation_profile_hash"][:12],
                row["exported_nodes"],
                row["error_count"],
                row["warning_count"],
                row["import_status"],
                Path(row["output_path"]).name,
                row["timestamp"],
            )
        )


def handle_publish(args: argparse.Namespace) -> None:
    """
    Handles the 'publish' command: runs the full translation pipeline and records results in the registry

    Args:
        args: Parsed CLI arguments
    """
    adapter = resolve_adapter(args.dcc, "publish")
    profile_path = resolve_profile(args.target)
    output_path = Path(args.out)

    if args.backend == "sqlite":
        db_path = Path(args.db)
    else:
        db_path = None

    run_translation_pipeline(
        adapter=adapter,
        profile_path=profile_path,
        output_path=str(output_path),
        backend=args.backend,
        db_path=str(db_path) if db_path else None,
    )

    info(f"Publish completed: {output_path}")

    registry = TranslationRegistry(
        backend=args.backend,
        db_path=str(db_path) if db_path else None,
    )

    rows = registry.fetch_translations()

    if rows:
        print_registry_table(rows[-5:])


def handle_validate(args: argparse.Namespace) -> None:
    """
    Handles the 'validate' command: runs validation only and prints results to console

    Args:
        args: Parsed CLI arguments
    """
    profile_path = resolve_profile(args.target)
    adapter = resolve_adapter(args.dcc, "validate")

    rules = ValidationProfileLoader.load_file(profile_path)
    validator = SceneValidator(rules)

    scene_nodes = adapter.extract_scene_nodes(rules)
    report = validator.validate(scene_nodes)

    print("Validation completed")

    if report.errors:
        print("Errors:")
        for err in report.errors:
            print(f" - {err}")

    if report.warnings:
        print("\nWarnings:")
        for warn in report.warnings:
            print(f" - {warn}")

    if report.blocking:
        print("Scene failed validation")
    else:
        print("Scene passed validation")


def handle_inspect(args: argparse.Namespace) -> None:
    """
    Handles the 'inspect' command: fetches and prints publish records from the registry

    Args:
        args: Parsed CLI arguments
    """
    try:
        backend = args.backend if args.backend else select_registry_backend()
    except Exception as e:
        print(f"Registry backend unavailable: {e}")
        return

    registry = TranslationRegistry(
        backend=backend,
        db_path=args.db if backend == "sqlite" else None,
    )

    rows = registry.fetch_translations()

    if not rows:
        print("No publish records found")
        return

    print_registry_table(rows)


def main() -> None:
    """
    Entry point for the CLI application
    """

    parser = argparse.ArgumentParser(
        prog="dcc-translate",
        description="DCC Translation Pipeline CLI",
    )

    subparsers = parser.add_subparsers(dest="command")

    # Publish command
    publish_parser = subparsers.add_parser(
        "publish",
        help="Run full publish pipeline",
    )

    publish_parser.add_argument("--dcc", default="maya")
    publish_parser.add_argument("--target", required=True)

    publish_parser.add_argument(
        "--backend",
        default="sqlite",
        choices=["sqlite", "mongo"],
    )

    publish_parser.add_argument("--out", required=True)
    publish_parser.add_argument("--db", default="translations.db")

    publish_parser.set_defaults(func=handle_publish)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Run validation only",
    )

    validate_parser.add_argument("--dcc", default="maya")
    validate_parser.add_argument("--target", required=True)

    validate_parser.set_defaults(func=handle_validate)

    # Inspect command
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect publish registry",
    )

    inspect_parser.add_argument(
        "--backend",
        default="sqlite",
        choices=["sqlite", "mongo"],
    )

    inspect_parser.add_argument("--db", default="translations.db")
    inspect_parser.set_defaults(func=handle_inspect)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

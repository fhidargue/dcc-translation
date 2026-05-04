import sys
from pathlib import Path
from dcc_translation.utils.maya_logging import info, warning, error

import maya.api.OpenMaya as om
import maya.cmds as cmds
import importlib

# Important: this flag is crucial when importing the plugin
maya_useNewAPI = True

CMD_NAME = "DCCExportUSD"

class DCCExportUSD(om.MPxCommand):
    def __init__(self):
        super().__init__()

    def doIt(self, args):
        """
        Executed when command runs inside Maya
        """

        try:
            from dcc_translation.adapters.maya_adapter import MayaAdapter
            from dcc_translation.core.pipeline import run_translation_pipeline
            from dcc_translation.cli.cli import resolve_profile
            from dcc_translation.utils.backend_detection import select_registry_backend

            # Ensure project root available
            plugin_path = cmds.pluginInfo("DCCExportUSD.py", query=True, path=True)
            project_root = Path(plugin_path).parents[2]

            if str(project_root) not in sys.path:
                sys.path.append(str(project_root))
                info("- Project root added to sys.path")

            for module in list(sys.modules):
                if module.startswith("dcc_translation"):
                    importlib.reload(sys.modules[module])

            output_path = cmds.fileDialog2(
                fileMode=0,
                caption="Export USD to Unreal",
                fileFilter="USD Files (*.usd *.usda *.usdc)"
            )

            info("Reloaded pipeline modules")

            if not output_path:
                warning("Publish was cancelled, please check the file name and extension")
                return

            output_path = Path(output_path[0])

            if output_path.suffix.lower() not in [".usd", ".usda", ".usdc"]:
                output_path = output_path.with_suffix(".usd")

            output_path = str(output_path)

            info("Resolving validation profile")

            profile_path = resolve_profile("unreal")

            info(f"- Using profile: {Path(profile_path).name}")

            info("Detecting registry backend")

            backend = select_registry_backend()

            info(f"- Detected backend: {backend}")

            info("Running translation pipeline")

            adapter = MayaAdapter()

            run_translation_pipeline(
                adapter=adapter,
                profile_path=profile_path,
                output_path=output_path,
                backend=backend,
                db_path=(
                    str(Path(output_path).with_suffix(".db"))
                    if backend == "sqlite"
                    else None
                ),
            )

            info(f"- Export completed: {output_path}")
            info("Publish complete")
        except Exception as e:
            error(f"Publish failed: {e}")

            
    @classmethod
    def creator(cls):
        return cls()


def initializePlugin(plugin):
    """
    Load the plugin
    """

    vendor = "Felipe Hidalgo"
    version = "1.0.0"

    plugin_fn = om.MFnPlugin(plugin, vendor, version)

    try:
        plugin_fn.registerCommand(
            CMD_NAME,
            DCCExportUSD.creator
        )
        info(f"{CMD_NAME} command registered")
    except Exception as e:
        error(
            f"Failed to register command: {CMD_NAME} ({e})"
        )


def uninitializePlugin(plugin):
    """
    Unload the plugin
    """

    plugin_fn = om.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterCommand(CMD_NAME)
        info(f"{CMD_NAME} command deregistered")
    except Exception as e:
        error(
            f"Failed to deregister command: {CMD_NAME} ({e})"
        )
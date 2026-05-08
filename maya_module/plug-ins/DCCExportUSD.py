import sys
from pathlib import Path
from dcc_translation.utils.maya_logging import info, error
from maya_module.utils.constants import PLUGIN_NAME, COMMAND_NAME

import maya.api.OpenMaya as om
import maya.cmds as cmds
import importlib

# Important: this flag is crucial when importing the plugin
maya_useNewAPI = True


class DCCExportUSD(om.MPxCommand):
    def __init__(self):
        super().__init__()

    def doIt(self, args: om.MArgList) -> None:
        """
        Launch validation UI

        Args:
            args: Command arguments
        """

        try:
            # Ensure project root available
            plugin_path = cmds.pluginInfo(f"{PLUGIN_NAME}", query=True, path=True)
            project_root = Path(plugin_path).parents[2]

            if str(project_root) not in sys.path:
                sys.path.append(str(project_root))
                info("Project root added to sys.path")

            for module in list(sys.modules):
                if module.startswith("dcc_translation"):
                    importlib.reload(sys.modules[module])

            info("Reloaded pipeline modules")

            # Import validation window after reloading modules
            from dcc_translation.ui.validation_window import (
                ValidationWindow,
            )

            global validation_window

            try:
                if validation_window:
                    validation_window.close()
                    validation_window.deleteLater()

            except NameError:
                pass
            except Exception as e:
                error(f"Failed to close validation window: {e}")

            validation_window = ValidationWindow()
            validation_window.show(dockable=True)

            info("Opened Validation Window")
        except Exception as e:
            error(f"Failed to open validation UI: {e}")

    @classmethod
    def creator(cls):
        return cls()


def initializePlugin(plugin: om.MObject) -> None:
    """
    Load the plugin

    Args:
        plugin: The Maya plugin object passed in by Maya when loading the plugin
    """

    vendor = "Felipe Hidalgo"
    version = "1.0.0"

    plugin_fn = om.MFnPlugin(plugin, vendor, version)

    try:
        plugin_fn.registerCommand(COMMAND_NAME, DCCExportUSD.creator)
        info(f"{COMMAND_NAME} command registered")
    except Exception as e:
        error(f"Failed to register command: {COMMAND_NAME} ({e})")


def uninitializePlugin(plugin: om.MObject) -> None:
    """
    Unload the plugin

    Args:
        plugin: The Maya plugin object passed in by Maya when unloading the plugin
    """

    plugin_fn = om.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterCommand(COMMAND_NAME)
        info(f"{COMMAND_NAME} command deregistered")
    except Exception as e:
        error(f"Failed to deregister command: {COMMAND_NAME} ({e})")

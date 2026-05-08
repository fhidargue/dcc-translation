import sys
import maya.cmds as cmds
import maya.mel as mel

from pathlib import Path
from maya_module.utils.utils import (
    get_maya_root,
    get_maya_version,
    get_modules_dir,
    get_main_shelves_layout,
    get_shelf_button,
)
from maya_module.utils.constants import (
    PLUGIN_NAME,
    MODULE_NAME,
    MODULE_VERSION,
    SHELF_NAME,
    BUTTON_ANNOTATION,
    BUTTON_ICON,
    BUTTON_LABEL,
    COMMAND_NAME,
    REPLACE_LABEL,
)
from maya_module.utils.enums import Answers
from dcc_translation.utils.maya_logging import info, warning


def write_module_file(modules_dir: Path) -> None:
    project_root = Path(__file__).resolve().parent
    module_path = modules_dir / f"{MODULE_NAME}.mod"

    if module_path.exists():
        response = cmds.confirmDialog(
            title=REPLACE_LABEL,
            message=f"{module_path.name} already exists.\nReplace it?",
            button=[Answers.YES.value, Answers.NO.value],
            defaultButton=Answers.YES.value,
            cancelButton=Answers.NO.value,
            dismissString=Answers.NO.value,
        )

        if response != Answers.YES.value:
            warning("Installation cancelled")
            return

    info(f"Writing module file to: {module_path}")

    with open(module_path, "w") as file:
        file.write(f"+ {MODULE_NAME} {MODULE_VERSION} {project_root}\n")
        file.write("PYTHONPATH +:= .\n")
        file.write("MAYA_PLUG_IN_PATH +:= maya_module/plug-ins\n")
        file.write("XBMLANGPATH +:= maya_module/plug-ins/icons\n")
        file.write("MAYA_SCRIPT_PATH +:= maya_module/scripts\n")

    info(f"Module {MODULE_NAME} installed successfully")


def load_plugin() -> None:
    """
    Load export plugin
    """

    plugin_path = (
        Path(__file__).resolve().parent / "maya_module" / "plug-ins" / PLUGIN_NAME
    )

    if not plugin_path.exists():
        raise FileNotFoundError(f"Plugin not found: {str(plugin_path)}")

    if cmds.pluginInfo(
        PLUGIN_NAME,
        query=True,
        loaded=True,
    ):
        try:
            cmds.unloadPlugin(PLUGIN_NAME)
        except Exception:
            pass

    cmds.loadPlugin(str(plugin_path))

    cmds.pluginInfo(PLUGIN_NAME, edit=True, autoload=True)

    info(f"Loaded plugin: {PLUGIN_NAME}")


def create_shelf() -> None:
    """
    Create export shelf
    """

    shelves_layout = get_main_shelves_layout()

    # Create shelf if needed
    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        cmds.setParent(shelves_layout)
        cmds.shelfLayout(SHELF_NAME, parent=shelves_layout)
        cmds.tabLayout(shelves_layout, edit=True, tabLabel=(SHELF_NAME, SHELF_NAME))

    existing_button = get_shelf_button(SHELF_NAME, BUTTON_LABEL)
    button_command = f"import maya.cmds as cmds; cmds.{COMMAND_NAME}()"

    # Update existing button
    if existing_button:
        cmds.shelfButton(
            existing_button,
            edit=True,
            command=button_command,
            annotation=BUTTON_ANNOTATION,
            image1=BUTTON_ICON,
        )
        info("Updated existing shelf button")

    # Create new button
    else:
        cmds.shelfButton(
            label=BUTTON_LABEL,
            annotation=BUTTON_ANNOTATION,
            image1=BUTTON_ICON,
            command=button_command,
            sourceType="python",
            parent=SHELF_NAME,
            width=32,
            height=32,
            style="iconOnly",
        )
        info("Created new shelf button")
    cmds.refresh()


def install_module() -> None:
    root = get_maya_root()
    version_dir = get_maya_version(root)
    modules_dir = get_modules_dir(version_dir)

    info(f"Maya root: {root}")
    info(f"Maya version: {version_dir.name}")
    info(f"Modules dir: {modules_dir}")

    write_module_file(modules_dir)


def onMayaDroppedPythonFile(*args: list) -> None:
    """
    Maya drag and drop installer
    """

    try:
        # Clear cached installer modules
        sys.modules.pop("drag_to_maya", None)

        info("=" * 60)
        info("Installing DCC Translation Pipeline")
        info("=" * 60)

        # Install the package module
        install_module()

        # Force Maya to refresh env variables
        mel.eval("rehash")
        cmds.loadModule(allModules=True)

        # Reload the plugin and create the shelf
        load_plugin()
        create_shelf()

        cmds.refresh(force=True)

        info("DCC Translation installation complete")
    except Exception as e:
        warning(f"Installation failed: {e}")

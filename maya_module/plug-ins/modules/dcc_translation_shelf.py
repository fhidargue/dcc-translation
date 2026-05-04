import maya.cmds as cmds
import maya.mel as mel

BUTTON_NAME = "dcc_translation_export_button"
ICON_NAME = "dcc_translation_icon.png"
SHELF_NAME = "DCCTranslation"


def create_shelf():
    """
    Create Maya shelf with export button
    """

    if not cmds.shelfLayout(SHELF_NAME, exists=True):
        mel.eval(f'addNewShelfTab "{SHELF_NAME}"')

    if cmds.shelfButton(BUTTON_NAME, exists=True):
        cmds.deleteUI(BUTTON_NAME)

    cmds.shelfButton(
        BUTTON_NAME,
        parent=SHELF_NAME,
        label="Export USD File",
        annotation="Export USD to Unreal",
        image=ICON_NAME,
        width=32,
        height=32,
        command="import maya.cmds as cmds; cmds.DCCExportUSD()",
    )


def load():
    """
    Entry point called from userSetup.py
    """

    cmds.evalDeferred(create_shelf)
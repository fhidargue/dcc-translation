from pathlib import Path

import maya.cmds as cmds
from maya.app.general.mayaMixin import (
    MayaQWidgetDockableMixin,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dcc_translation.controllers.validation_controller import (
    validate_scene,
)
from dcc_translation.ui.rule_renderer import (
    render_rule,
)
from dcc_translation.ui.validation_profile_model import (
    ValidationProfileModel,
)
from dcc_translation.utils.maya_logging import (
    info,
)
from dcc_translation.utils.utils import (
    get_validation_field_label,
)
from dcc_translation.utils.enums import (
    LogTypes,
)

QTIMER_DELAY = 100


class ValidationWindow(
    MayaQWidgetDockableMixin,
    QWidget,
):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DCC Translation Validation Profiles")

        self.resize(700, 500)

        self.profile_dirty = False
        self.validation_passed = False

        profile_path = (
            Path(__file__).resolve().parents[1]
            / "validation_profiles"
            / "maya_to_unreal.yml"
        )

        default_profile_path = (
            Path(__file__).resolve().parents[1]
            / "validation_profiles"
            / "maya_to_unreal.default.yml"
        )

        self.model = ValidationProfileModel(
            str(profile_path), str(default_profile_path)
        )

        self.profile_data = self.model.load()

        self.build_ui()
        self.populate_rules()

    def build_ui(self) -> None:
        """
        Build Qt UI
        """

        # Main layouts
        self.main_layout = QVBoxLayout(self)

        self.content_layout = QHBoxLayout()

        # Rule list
        self.rules_list = QListWidget()

        # Details panel
        self.details_widget = QWidget()

        self.details_layout = QVBoxLayout(self.details_widget)

        # Main split layout
        self.content_layout.addWidget(
            self.rules_list,
            1,
        )

        self.content_layout.addWidget(
            self.details_widget,
            2,
        )

        self.main_layout.addLayout(self.content_layout)

        # Output console
        self.output_console = QTextEdit()

        self.output_console.setReadOnly(True)

        self.main_layout.addWidget(self.output_console)

        # Bottom buttons
        buttons_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Profile")

        self.reload_button = QPushButton("Reset Profile")

        self.validate_button = QPushButton("Validate Scene")

        self.publish_button = QPushButton("Publish USD")
        self.publish_button.setEnabled(False)

        buttons_layout.addWidget(self.save_button)

        buttons_layout.addWidget(self.reload_button)

        buttons_layout.addWidget(self.validate_button)

        buttons_layout.addWidget(self.publish_button)

        self.main_layout.addLayout(buttons_layout)

        # Signals
        self.rules_list.currentItemChanged.connect(self.display_rule_details)

        self.save_button.clicked.connect(self.save_profile)

        self.reload_button.clicked.connect(self.reset_profile)

        self.validate_button.clicked.connect(self.validate_scene)

        self.publish_button.clicked.connect(self.publish_scene)

        # UI Styling
        self.main_layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        self.content_layout.setSpacing(16)

        self.details_layout.setAlignment(Qt.AlignTop)
        self.details_layout.setSpacing(12)
        self.details_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        self.rules_list.setMinimumWidth(220)
        self.rules_list.setMaximumWidth(260)

        self.output_console.setMinimumHeight(160)

    def populate_rules(self) -> None:
        """
        Populate validation rule list
        """

        self.rules_list.clear()

        for rule_name in self.profile_data:
            display_name = get_validation_field_label(rule_name)

            item = QListWidgetItem(display_name)

            item.setData(
                Qt.UserRole,
                rule_name,
            )

            self.rules_list.addItem(item)

    def clear_layout(
        self,
        layout,
    ) -> None:
        """
        Clear all widgets from layout

        Args:
            layout (QLayout): The layout to clear
        """

        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

    def log_output(
        self,
        message: str,
        level: LogTypes = LogTypes.INFO.value,
    ) -> None:
        """
        Write formatted output to console

        Args:
            message (str): Message to display
            level (LogTypes): Log level
        """

        level = level.upper()
        prefixes = {
            LogTypes.INFO.value: "[INFO]",
            LogTypes.SUCCESS.value: "[SUCCESS]",
            LogTypes.WARNING.value: "[WARNING]",
            LogTypes.ERROR.value: "[ERROR]",
            LogTypes.SECTION.value: "=" * 60,
        }

        if level == LogTypes.SECTION.value:
            formatted_message = f"\n{prefixes[level]}\n{message}\n{prefixes[level]}"
        else:
            formatted_message = f"{prefixes.get(level, '[INFO]')} {message}"

        self.output_console.append(formatted_message.rstrip())

    def set_validation_state(
        self,
        passed,
    ) -> None:
        """
        Track validation state

        Args:
            passed (bool): Whether validation passed or failed
        """

        self.validation_passed = passed

        self.publish_button.setEnabled(passed)

    def set_profile_dirty(
        self,
        dirty=True,
    ) -> None:
        """
        Track unsaved profile changes

        Args:
            dirty (bool): Whether the profile has unsaved changes
        """

        self.profile_dirty = dirty

        title = "DCC Translation Validation Profiles"

        if dirty:
            title += " *"

        self.setWindowTitle(title)

    def save_profile(self) -> None:
        """
        Save YAML profile
        """

        self.model.data = self.profile_data

        self.model.save()

        self.set_profile_dirty(False)
        self.output_console.clear()
        self.log_output("Validation profile saved", LogTypes.SUCCESS.value)

        info("Validation profile saved")

    def reset_profile(self) -> None:
        """
        Reset YAML profile to defaults
        """

        self.profile_data = self.model.reset_to_defaults()

        self.populate_rules()

        self.clear_layout(self.details_layout)

        self.set_profile_dirty(False)
        self.set_validation_state(False)
        self.output_console.clear()

        self.log_output(
            "Validation profile reset to defaults",
            LogTypes.SUCCESS.value,
        )

        info("Validation profile reset to defaults")

    def run_validation(self) -> None:
        """
        Execute validation
        """

        try:
            report = validate_scene(self.profile_data)

            # Errors
            if report.errors:
                for error in report.errors:
                    self.log_output(f"{error}", LogTypes.ERROR.value)

            # Warnings
            if report.warnings:
                for warning in report.warnings:
                    self.log_output(f"{warning}", LogTypes.WARNING.value)

            # Final status
            if report.blocking:
                self.set_validation_state(False)
                self.log_output("Validation failed", LogTypes.ERROR.value)
            else:
                self.set_validation_state(True)
                self.log_output("Validation passed", LogTypes.SUCCESS.value)
        except Exception as error:
            self.log_output(f"Validation crashed: {error}", LogTypes.ERROR.value)
        finally:
            self.validate_button.setEnabled(True)
            self.publish_button.setEnabled(self.validation_passed)

    def run_publish(self) -> None:
        """
        Execute publish
        """

        from dcc_translation.controllers.publish_controller import (
            publish_scene as execute_publish,
        )

        try:
            output_path = cmds.fileDialog2(
                fileMode=0,
                caption="Export USD",
                fileFilter=("USD Files (*.usd *.usda *.usdc)"),
            )

            if not output_path:
                self.log_output("Publish cancelled", LogTypes.INFO.value)

                return

            # Ensure correct file extension
            output_path = Path(output_path[0])

            if output_path.suffix.lower() not in [
                ".usd",
                ".usda",
                ".usdc",
            ]:
                output_path = output_path.with_suffix(".usd")

            output_path = str(output_path)

            # Publish
            result = execute_publish(output_path)

            self.log_output(f"Output: {result['output_path']}", LogTypes.INFO.value)
            self.log_output(f"Backend: {result['backend']}", LogTypes.INFO.value)
            self.log_output("Publish complete", LogTypes.SUCCESS.value)

        except Exception as error:
            self.log_output(f"Publish failed: {error}", LogTypes.ERROR.value)

        finally:
            self.validate_button.setEnabled(True)

            self.publish_button.setEnabled(self.validation_passed)

    def validate_scene(self) -> None:
        """
        Run scene validation
        """

        self.save_profile()

        self.output_console.clear()

        self.log_output("Running validation", LogTypes.INFO.value)

        self.validate_button.setEnabled(False)
        self.set_validation_state(False)

        QTimer.singleShot(
            QTIMER_DELAY,
            self.run_validation,
        )

    def publish_scene(self) -> None:
        """
        Validate and publish USD
        """

        self.save_profile()

        self.output_console.clear()

        self.log_output("Starting publish", LogTypes.INFO.value)

        self.publish_button.setEnabled(False)
        self.validate_button.setEnabled(False)

        QTimer.singleShot(
            QTIMER_DELAY,
            self.run_publish,
        )

    def update_profile_value(
        self,
        rule_name: str,
        key: str | None,
        value: str | bool | list | dict,
    ) -> None:
        """
        Update in-memory profile data

        Args:
            rule_name (str): The name of the validation rule to update
            key (str): The specific field within the rule to update (can be None for top-level fields)
            value: The new value to set for the specified rule and key
        """

        if key is not None and isinstance(
            self.profile_data.get(rule_name),
            dict,
        ):
            self.profile_data[rule_name][key] = value

            info(f"Updated {rule_name}.{key} = {value}")

        else:
            self.profile_data[rule_name] = value

            info(f"Updated {rule_name} = {value}")

        self.set_profile_dirty(True)
        self.set_validation_state(False)

    def sync_list_widget(
        self,
        rule_name: str,
        key: str | None,
        list_widget: QListWidget,
    ) -> None:
        """
        Sync QListWidget values into profile data

        Args:
            rule_name (str): The name of the validation rule to update
            key (str): The specific field within the rule to update
            list_widget (QListWidget): The QListWidget instance containing the list values to sync
        """

        values = []

        for index in range(list_widget.count()):
            item = list_widget.item(index)

            values.append(item.text())

        self.update_profile_value(
            rule_name,
            key,
            values,
        )

    def create_editable_list_widget(
        self,
        values: list,
        rule_name: str,
        key: str | None = None,
    ) -> QWidget:
        """
        Create editable list widget

        Args:
            values (list): The list of values to populate the widget with
            rule_name (str): The name of the validation rule to update when values change
            key (str | None): The specific field within the rule to update (can be None for top-level list rules)
        """

        container = QWidget()

        layout = QVBoxLayout(container)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        list_widget = QListWidget()

        list_widget.setAlternatingRowColors(True)

        list_widget.setEditTriggers(QAbstractItemView.DoubleClicked)

        # Populate items
        for value in values:
            item = QListWidgetItem(str(value))

            item.setFlags(item.flags() | Qt.ItemIsEditable)

            list_widget.addItem(item)

        # Buttons row
        buttons_row = QWidget()

        buttons_layout = QHBoxLayout(buttons_row)

        buttons_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        add_button = QPushButton("Add")

        remove_button = QPushButton("Remove")

        buttons_layout.addWidget(add_button)

        buttons_layout.addWidget(remove_button)

        def add_list_item() -> None:
            """
            Adds an item to the list widget
            """

            item = QListWidgetItem("new_item")

            item.setFlags(item.flags() | Qt.ItemIsEditable)

            list_widget.addItem(item)

            self.sync_list_widget(
                rule_name,
                key,
                list_widget,
            )

        def remove_list_item() -> None:
            """
            Removes an item from the list widget
            """

            current_item = list_widget.currentItem()

            if not current_item:
                return

            row = list_widget.row(current_item)

            list_widget.takeItem(row)

            self.sync_list_widget(
                rule_name,
                key,
                list_widget,
            )

        add_button.clicked.connect(add_list_item)

        remove_button.clicked.connect(remove_list_item)

        list_widget.itemChanged.connect(
            lambda: self.sync_list_widget(
                rule_name,
                key,
                list_widget,
            )
        )

        layout.addWidget(list_widget)

        layout.addWidget(buttons_row)

        return container

    def display_rule_details(
        self,
        current: QListWidgetItem,
        previous: QListWidgetItem = None,
    ) -> None:
        """
        Build dynamic widgets

        Args:
            current (QListWidgetItem): The currently selected rule item
            previous (QListWidgetItem): The previously selected rule item
        """

        self.clear_layout(self.details_layout)

        if not current:
            return

        rule_name = current.data(Qt.UserRole)

        value = self.profile_data.get(rule_name)

        render_rule(
            self,
            self.details_layout,
            rule_name,
            value,
        )

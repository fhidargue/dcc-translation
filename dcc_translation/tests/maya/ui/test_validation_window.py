import pytest
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
)

from dcc_translation.ui.validation_window import ValidationWindow

pytestmark = pytest.mark.maya

# Ensure QApplication exists
app = QApplication.instance()

if not app:
    app = QApplication([])


class MockReport:
    def __init__(
        self,
        errors=None,
        warnings=None,
        blocking=False,
    ):
        self.errors = errors or []
        self.warnings = warnings or []
        self.blocking = blocking


@pytest.fixture
def window(monkeypatch):
    """
    Create validation window
    """

    monkeypatch.setattr(
        "dcc_translation.ui.validation_window.ValidationProfileModel.load",
        lambda *_: {
            "unit_scale": "cm",
            "require_geometry": {
                "enabled": True,
            },
        },
    )

    monkeypatch.setattr(
        "dcc_translation.ui.validation_window.ValidationProfileModel.save",
        lambda *_: None,
    )

    window = ValidationWindow()

    yield window

    window.close()
    window.deleteLater()


def test_publish_button_disabled(window):
    """
    Publish button starts disabled
    """

    assert not window.publish_button.isEnabled()


def test_validation_enables_publish(window):
    """
    Validation success enables publish
    """

    window.set_validation_state(True)

    assert window.publish_button.isEnabled()
    assert window.validation_passed is True


def test_validation_disables_publish(window):
    """
    Validation failure disables publish
    """

    window.set_validation_state(False)

    assert not window.publish_button.isEnabled()
    assert window.validation_passed is False


def test_profile_edit_invalidates_validation(window):
    """
    Editing profile disables publish state
    """

    window.set_validation_state(True)

    assert window.publish_button.isEnabled()

    window.update_profile_value(
        "unit_scale",
        None,
        "m",
    )

    assert not window.publish_button.isEnabled()
    assert window.validation_passed is False


def test_profile_dirty_state(window):
    """
    Dirty state updates title
    """

    window.set_profile_dirty(True)

    assert "*" in window.windowTitle()

    window.set_profile_dirty(False)

    assert "*" not in window.windowTitle()


def test_log_output(window):
    """
    Output console receives text
    """

    window.log_output("Hello")

    output = window.output_console.toPlainText()

    assert "Hello" in output


def test_validation_success(
    window,
    monkeypatch,
):
    """
    Successful validation enables publish
    """

    monkeypatch.setattr(
        "dcc_translation.ui.validation_window.validate_scene",
        lambda *_: MockReport(
            errors=[],
            warnings=[],
            blocking=False,
        ),
    )

    window.run_validation()

    output = window.output_console.toPlainText()

    assert "Validation passed" in output
    assert window.publish_button.isEnabled()
    assert window.validation_passed is True


def test_validation_failure(
    window,
    monkeypatch,
):
    """
    Failed validation disables publish
    """

    monkeypatch.setattr(
        "dcc_translation.ui.validation_window.validate_scene",
        lambda *_: MockReport(
            errors=["Invalid transform"],
            warnings=[],
            blocking=True,
        ),
    )

    window.run_validation()

    output = window.output_console.toPlainText()

    assert "Validation failed" in output
    assert "Invalid transform" in output

    assert not window.publish_button.isEnabled()
    assert window.validation_passed is False


def test_validation_warnings(
    window,
    monkeypatch,
):
    """
    Validation warnings appear in output
    """

    monkeypatch.setattr(
        "dcc_translation.ui.validation_window.validate_scene",
        lambda *_: MockReport(
            errors=[],
            warnings=["Non-critical issue"],
            blocking=False,
        ),
    )

    window.run_validation()

    output = window.output_console.toPlainText()

    assert "Warnings:" in output
    assert "Non-critical issue" in output


def test_validation_exception(
    window,
    monkeypatch,
):
    """
    Validation exceptions are handled
    """

    def mock_validate(*_):
        raise RuntimeError("Validation crash")

    monkeypatch.setattr(
        "dcc_translation.ui.validation_window.validate_scene",
        mock_validate,
    )

    window.run_validation()

    output = window.output_console.toPlainText()

    assert "Validation crashed" in output
    assert "Validation crash" in output


def test_reload_resets_state(
    window,
    monkeypatch,
):
    """
    Reload resets dirty and validation states
    """

    monkeypatch.setattr(
        "dcc_translation.ui.validation_window.ValidationProfileModel.load",
        lambda *_: {
            "unit_scale": "m",
        },
    )

    window.set_profile_dirty(True)
    window.set_validation_state(True)

    window.reload_profile()

    assert window.profile_dirty is False
    assert window.validation_passed is False
    assert not window.publish_button.isEnabled()


def test_sync_list_widget_updates(window):
    """
    List widget sync updates profile data
    """

    list_widget = QListWidget()

    list_widget.addItem("mesh")
    list_widget.addItem("transform")

    window.sync_list_widget(
        "allowed_node_types",
        None,
        list_widget,
    )

    assert window.profile_data["allowed_node_types"] == [
        "mesh",
        "transform",
    ]


def test_update_nested_profile_value(window):
    """
    Nested dict values update correctly
    """

    window.profile_data["require_geometry"] = {
        "enabled": True,
    }

    window.update_profile_value(
        "require_geometry",
        "enabled",
        False,
    )

    assert window.profile_data["require_geometry"]["enabled"] is False


def test_display_rule_details(
    window,
    monkeypatch,
):
    """
    Rule rendering executes safely
    """

    item = window.rules_list.item(0)

    monkeypatch.setattr(
        "dcc_translation.ui.validation_window.render_rule",
        lambda *_: None,
    )

    window.display_rule_details(item)

    assert item is not None

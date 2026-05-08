import pytest

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QWidget,
)

from dcc_translation.ui.widget_factory import (
    create_checkbox,
    create_line_edit,
    create_combo_box,
    create_row_widget,
)

pytestmark = pytest.mark.maya

# Ensure QApplication exists
app = QApplication.instance()

if not app:
    app = QApplication([])


def test_create_checkbox_default_state():
    """
    Checkbox initializes correctly
    """

    checkbox = create_checkbox(
        "Enabled",
        True,
        lambda *_: None,
    )

    assert isinstance(checkbox, QCheckBox)

    assert checkbox.text() == "Enabled"

    assert checkbox.isChecked() is True

    checkbox.deleteLater()


def test_create_checkbox_unchecked():
    """
    Checkbox supports unchecked state
    """

    checkbox = create_checkbox(
        "Disabled",
        False,
        lambda *_: None,
    )

    assert checkbox.isChecked() is False

    checkbox.deleteLater()


def test_checkbox_callback():
    """
    Checkbox callback executes
    """

    state = {
        "value": None,
    }

    def callback(value):
        state["value"] = value

    checkbox = create_checkbox(
        "Enabled",
        False,
        callback,
    )

    checkbox.setChecked(True)

    assert state["value"] is True

    checkbox.deleteLater()


def test_create_line_edit_default_text():
    """
    Line edit initializes correctly
    """

    line_edit = create_line_edit(
        "hello",
        lambda *_: None,
    )

    assert isinstance(line_edit, QLineEdit)

    assert line_edit.text() == "hello"

    line_edit.deleteLater()


def test_line_edit_callback():
    """
    Line edit callback executes
    """

    result = {
        "value": None,
    }

    def callback(value):
        result["value"] = value

    line_edit = create_line_edit(
        "initial",
        callback,
    )

    line_edit.setText("updated")

    assert result["value"] == "updated"

    line_edit.deleteLater()


def test_create_combo_box():
    """
    Combo box initializes correctly
    """

    combo = create_combo_box(
        [
            "cm",
            "m",
            "mm",
        ],
        "m",
        lambda *_: None,
    )

    assert isinstance(combo, QComboBox)

    assert combo.count() == 3

    assert combo.currentText() == "m"

    combo.deleteLater()


def test_combo_box_callback():
    """
    Combo box callback executes
    """

    result = {
        "value": None,
    }

    def callback(value):
        result["value"] = value

    combo = create_combo_box(
        [
            "cm",
            "m",
        ],
        "cm",
        callback,
    )

    combo.setCurrentText("m")

    assert result["value"] == "m"

    combo.deleteLater()


def test_create_row_widget():
    """
    Row widget contains label and widget
    """

    line_edit = QLineEdit()

    row = create_row_widget(
        "Unit Scale",
        line_edit,
    )

    assert isinstance(row, QWidget)

    layout = row.layout()

    assert layout.count() == 2

    label = layout.itemAt(0).widget()
    field = layout.itemAt(1).widget()

    assert isinstance(label, QLabel)
    assert label.text() == "Unit Scale"
    assert field == line_edit

    row.deleteLater()


def test_combo_box_values():
    """
    Combo box preserves item ordering
    """

    values = [
        "low",
        "medium",
        "high",
    ]

    combo = create_combo_box(
        values,
        "medium",
        lambda *_: None,
    )

    combo_values = [combo.itemText(index) for index in range(combo.count())]

    assert combo_values == values

    combo.deleteLater()


def test_line_edit_empty_text():
    """
    Line edit supports empty strings
    """

    line_edit = create_line_edit(
        "",
        lambda *_: None,
    )

    assert line_edit.text() == ""

    line_edit.deleteLater()


def test_checkbox_signal_multiple_updates():
    """
    Checkbox callback updates multiple times
    """

    calls = []

    def callback(value):
        calls.append(value)

    checkbox = create_checkbox(
        "Test",
        False,
        callback,
    )

    checkbox.setChecked(True)
    checkbox.setChecked(False)

    assert calls == [
        True,
        False,
    ]

    checkbox.deleteLater()


def test_combo_box_signal_multiple_updates():
    """
    Combo callback updates multiple times
    """

    calls = []

    def callback(value):
        calls.append(value)

    combo = create_combo_box(
        [
            "a",
            "b",
            "c",
        ],
        "a",
        callback,
    )

    combo.setCurrentText("b")
    combo.setCurrentText("c")

    assert calls == [
        "b",
        "c",
    ]

    combo.deleteLater()

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QLineEdit,
    QComboBox,
)


def create_checkbox(
    label: str,
    value: bool,
    callback: callable,
) -> QCheckBox:
    """
    Create configured checkbox widget

    Args:
        label (str): The text label to display next to the checkbox
        value (bool): The initial checked state of the checkbox
        callback (function): The function to call when the checkbox state changes, receives new boolean state as argument
    """

    checkbox = QCheckBox(label)

    # Prevent firing signal when starting
    checkbox.blockSignals(True)
    checkbox.setChecked(value)
    checkbox.blockSignals(False)

    checkbox.stateChanged.connect(lambda state: callback(bool(state)))

    return checkbox


def create_line_edit(
    value: str,
    callback: callable,
) -> QLineEdit:
    """
    Create configured line edit widget

    Args:
        value (str): The initial text to display in the line edit
        callback (function): The function to call when the text changes, receives new text as argument
    """

    line_edit = QLineEdit(value)

    # Prevent firing signal when starting
    line_edit.blockSignals(True)
    line_edit.setText(value)
    line_edit.blockSignals(False)

    line_edit.textChanged.connect(callback)

    return line_edit


def create_combo_box(
    values: list,
    current_value: str,
    callback: callable,
) -> QComboBox:
    """
    Create configured combo box widget

    Args:
        values (list): The list of string values to populate the combo box with
        current_value (str): The initial value to set in the combo box
        callback (function): The function to call when the selected value changes, receives new value as argument
    """

    combo = QComboBox()

    combo.addItems(values)

    # Prevent firing signal when starting
    combo.blockSignals(True)
    combo.setCurrentText(current_value)
    combo.blockSignals(False)

    combo.currentTextChanged.connect(callback)

    return combo


def create_row_widget(
    label_text: str,
    widget: QWidget,
) -> QWidget:
    """
    Create horizontal row widget

    Args:
        label_text (str): The text to display in the label on the left side of the row
        widget (QWidget): The widget to display on the right side of the row
    """

    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(
        0,
        0,
        0,
        0,
    )

    layout.addWidget(QLabel(label_text))
    layout.addWidget(widget)

    return row

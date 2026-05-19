from PySide6.QtWidgets import QLabel, QWidget, QLayout, QSizePolicy

from dcc_translation.ui.widget_factory import (
    create_checkbox,
    create_line_edit,
    create_combo_box,
    create_row_widget,
)

from dcc_translation.utils.utils import (
    get_validation_field_label,
)

from dcc_translation.ui.validation_schema import (
    VALIDATION_FIELDS,
)

MAX_FIELD_WIDTH = 260


def style_widget(widget) -> None:
    """
    Apply consistent sizing/styling
    """

    widget.setMaximumWidth(MAX_FIELD_WIDTH)

    widget.setSizePolicy(
        QSizePolicy.Fixed,
        QSizePolicy.Fixed,
    )


def render_rule(
    window: QWidget,
    layout: QLayout,
    rule_name: str,
    value: str | bool | list | dict,
) -> None:
    """
    Render validation rule widgets

    Args:
        window (QWidget): The parent window for the widgets
        layout (QLayout): The layout to add the widgets to
        rule_name (str): The name of the validation rule
        value: The value of the validation rule (type determines widget)
    """

    layout.setSpacing(12)
    title = QLabel(get_validation_field_label(rule_name))
    title.setStyleSheet(
        """
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 8px;
        """
    )

    layout.addWidget(title)

    # Boolean
    if isinstance(value, bool):
        widget = render_boolean_field(
            window,
            rule_name,
            None,
            value,
        )

        layout.addWidget(widget)

    # String
    elif isinstance(value, str):
        widget = render_string_field(
            window,
            rule_name,
            None,
            value,
        )

        layout.addWidget(widget)

    # List
    elif isinstance(value, list):
        widget = window.create_editable_list_widget(
            value,
            rule_name,
            None,
        )

        layout.addWidget(widget)

    # Dictionary
    elif isinstance(value, dict):
        render_dict_field(
            window,
            layout,
            rule_name,
            value,
        )

    # Fallback
    else:
        layout.addWidget(QLabel(str(value)))

    layout.addStretch()


def render_dict_field(
    window: QWidget,
    layout: QLayout,
    rule_name: str,
    values: dict,
) -> None:
    """
    Render dictionary rule

    Args:
        window (QWidget): The parent window for the widgets
        layout (QLayout): The layout to add the widgets to
        rule_name (str): The name of the validation rule
        values (dict): The dictionary of values to render (key determines widget)
    """

    for key, item_value in values.items():
        display_label = get_validation_field_label(key)

        field_config = VALIDATION_FIELDS.get(key)

        # Boolean
        if isinstance(item_value, bool):
            if field_config and field_config.get("widget") == "checkbox":
                widget = render_boolean_field(
                    window,
                    rule_name,
                    key,
                    item_value,
                    display_label,
                )

                layout.addWidget(widget)

            else:
                layout.addWidget(QLabel(f"{display_label}: {item_value}"))

        # String
        elif isinstance(item_value, str):
            widget = render_string_field(
                window,
                rule_name,
                key,
                item_value,
                display_label,
                field_config,
            )

            layout.addWidget(widget)

        # List
        elif isinstance(item_value, list):
            layout.addWidget(QLabel(display_label))

            widget = window.create_editable_list_widget(
                item_value,
                rule_name,
                key,
            )

            layout.addWidget(widget)

        # Numbers
        elif isinstance(
            item_value,
            (int, float),
        ):
            layout.addWidget(QLabel(f"{display_label}: {item_value}"))

        # Fallback
        else:
            layout.addWidget(QLabel(f"{display_label}: {item_value}"))


def render_boolean_field(
    window: QWidget,
    rule_name: str,
    key: str,
    value: bool,
    label=None,
) -> None:
    """
    Render checkbox field

    Args:
        window (QWidget): The parent window for the widget
        rule_name (str): The name of the validation rule
        key (str): The key for the specific field within the rule (can be None for top-level boolean rules)
        value (bool): The current value of the boolean field
        label (str): An optional label to display next to the checkbox
    """

    label = label or get_validation_field_label(rule_name)

    widget = create_checkbox(
        label,
        value,
        lambda state: window.update_profile_value(
            rule_name,
            key,
            state,
        ),
    )

    style_widget(widget)

    return widget


def render_string_field(
    window: QWidget,
    rule_name: str,
    key: str,
    value: str,
    label=None,
    field_config=None,
) -> None:
    """
    Render string field

    Args:
        window (QWidget): The parent window for the widget
        rule_name (str): The name of the validation rule
        key (str): The key for the specific field within the rule (can be None for top-level string rules)
        value (str): The current value of the string field
        label (str): An optional label to display next to the field
        field_config (dict): Optional configuration for the field (e.g. widget type, combo box values)
    """

    # Combo box
    if field_config and field_config.get("widget") == "combo":
        widget = create_combo_box(
            field_config.get(
                "values",
                [],
            ),
            value,
            lambda new_value: window.update_profile_value(
                rule_name,
                key,
                new_value,
            ),
        )

    # Line edit
    else:
        widget = create_line_edit(
            value,
            lambda new_value: window.update_profile_value(
                rule_name,
                key,
                new_value,
            ),
        )

    style_widget(widget)

    # Top level string
    if label is None:
        return widget

    return create_row_widget(
        label,
        widget,
    )

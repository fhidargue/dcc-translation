VALIDATION_FIELDS = {
    "severity": {
        "widget": "combo",
        "label": "Severity",
        "values": [
            "error",
            "warning",
            "info",
        ],
    },
    "enabled": {"widget": "checkbox", "label": "Enabled"},
    "ignore_transforms_without_shapes": {
        "widget": "checkbox",
        "label": "Ignore Empty Transforms",
    },
    "allowed_node_types": {
        "label": "Allowed Node Types",
    },
    "forbidden_node_types": {
        "label": "Forbidden Node Types",
    },
}

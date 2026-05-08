from dcc_translation.ui.validation_schema import VALIDATION_FIELDS


def sanitize_usd_name(name: str) -> str:
    """
    Sanitize a string to be valid for use in USD

    Args:
        name (str): The string to sanitize
    """

    return name.split("|")[-1].replace(":", "_").replace("|", "_").replace(" ", "_")


def get_validation_field_label(key: str) -> str:
    """
    Return readable UI labels

    Args:
        key (str): The validation field key to get the label for
    """

    field_config = VALIDATION_FIELDS.get(key, {})

    return field_config.get("label", key.replace("_", " ").title())

import pytest

from dcc_translation.controllers.validation_controller import (
    validate_scene,
)

pytestmark = pytest.mark.maya


class MockReport:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.blocking = False

    def error(
        self,
        message,
    ):
        self.errors.append(message)
        self.blocking = True

    def warning(
        self,
        message,
    ):
        self.warnings.append(message)


@pytest.fixture
def valid_profile():
    """
    Basic valid validation profile
    """

    return {
        "require_geometry": {
            "enabled": True,
            "severity": "error",
        },
        "require_frozen_transforms": {
            "enabled": True,
            "severity": "warning",
        },
    }


def test_validate_scene_returns_report(
    valid_profile,
):
    """
    Validation returns report object
    """

    report = validate_scene(valid_profile)

    assert report is not None
    assert hasattr(report, "errors")
    assert hasattr(report, "warnings")
    assert hasattr(report, "blocking")


def test_validation_report_has_errors():
    """
    Errors are collected correctly
    """

    report = MockReport()
    report.error("Invalid geometry")

    assert len(report.errors) == 1
    assert "Invalid geometry" in report.errors
    assert report.blocking is True


def test_validation_report_has_warnings():
    """
    Warnings are collected correctly
    """

    report = MockReport()
    report.warning("Non-frozen transform")

    assert len(report.warnings) == 1
    assert "Non-frozen transform" in report.warnings
    assert report.blocking is False


def test_validation_disabled_rule():
    """
    Disabled validation rules are ignored
    """

    profile = {
        "require_geometry": {
            "enabled": False,
            "severity": "error",
        },
    }

    report = validate_scene(profile)

    assert report.errors == []


def test_error_severity_blocks():
    """
    Error severity creates blocking validation
    """

    report = MockReport()
    report.error("Critical issue")

    assert report.blocking is True


def test_warning_severity_does_not_block():
    """
    Warnings do not block validation
    """

    report = MockReport()
    report.warning("Minor issue")

    assert report.blocking is False


def test_validation_handles_empty_profile():
    """
    Empty profile validates safely
    """

    report = validate_scene({})

    assert report.errors == []
    assert report.warnings == []


def test_validation_handles_none_profile():
    """
    None profile validates safely
    """

    report = validate_scene(None)

    assert report is not None


def test_validation_multiple_errors():
    """
    Multiple errors accumulate
    """

    report = MockReport()
    report.error("Error 1")
    report.error("Error 2")

    assert len(report.errors) == 2
    assert report.blocking is True


def test_validation_multiple_warnings():
    """
    Multiple warnings accumulate
    """

    report = MockReport()
    report.warning("Warning 1")
    report.warning("Warning 2")

    assert len(report.warnings) == 2


def test_validation_error_and_warning():
    """
    Errors and warnings coexist correctly
    """

    report = MockReport()
    report.error("Critical")
    report.warning("Minor")

    assert len(report.errors) == 1
    assert len(report.warnings) == 1
    assert report.blocking is True


def test_validation_report_defaults():
    """
    Validation report initializes cleanly
    """

    report = MockReport()

    assert report.errors == []
    assert report.warnings == []
    assert report.blocking is False

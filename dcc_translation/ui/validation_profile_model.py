from pathlib import Path
import yaml


class ValidationProfileModel:
    def __init__(
        self,
        profile_path: str,
        default_profile_path: str | None = None,
    ):
        self.profile_path = profile_path
        self.default_profile_path = default_profile_path
        self.data = {}

    def reset_to_defaults(self) -> dict:
        """
        Reset active profile using default YAML values
        """

        if not self.default_profile_path:
            raise RuntimeError("No default profile configured")

        default_file = Path(self.default_profile_path)

        if not default_file.exists():
            raise FileNotFoundError(
                f"Default profile not found: {self.default_profile_path}"
            )

        # Read defaults
        with open(default_file, "r") as file:
            default_data = yaml.safe_load(file) or {}

        # Overwrite active profile data
        self.data = default_data

        # Write defaults into active profile
        with open(self.profile_path, "w") as file:
            yaml.safe_dump(
                self.data,
                file,
                sort_keys=False,
            )

        return self.data

    def load(self) -> dict:
        """
        Load YAML validation profile
        """

        profile_file = Path(self.profile_path)

        if not profile_file.exists():
            self.data = {}

            return self.data

        with open(profile_file, "r") as file:
            self.data = yaml.safe_load(file) or {}

        return self.data

    def save(self) -> None:
        """
        Save YAML validation profile
        """

        with open(self.profile_path, "w") as file:
            yaml.safe_dump(
                self.data,
                file,
                sort_keys=False,
            )

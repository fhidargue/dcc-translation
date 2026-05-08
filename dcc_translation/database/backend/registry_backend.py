class RegistryBackend:
    def store_translation(self, data: dict) -> None:
        raise NotImplementedError

    def fetch_translations(self) -> list[dict]:
        raise NotImplementedError

    def store_dependencies(self, records: list[dict]) -> None:
        raise NotImplementedError

    def fetch_dependencies(self, publish_id: str) -> list[dict]:
        raise NotImplementedError

    def store_validation_report(self, report_data: dict) -> None:
        raise NotImplementedError

    def fetch_validation_report(self, publish_id: str) -> dict | None:
        raise NotImplementedError

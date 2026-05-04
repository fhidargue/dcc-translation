class RegistryBackend:
    def store_translation(self, data: dict):
        raise NotImplementedError

    def fetch_translations(self):
        raise NotImplementedError

    def store_dependencies(self, records):
        raise NotImplementedError

    def fetch_dependencies(self, publish_id):
        raise NotImplementedError

    def store_validation_report(self, report_data):
        raise NotImplementedError

    def fetch_validation_report(self, publish_id):
        raise NotImplementedError

class BaseCSVModel:
    def __init__(self, file_service, rel_path: str, headers: list[str]):
        self.file_service = file_service
        self.rel_path = rel_path
        self.headers = headers

    def all(self):
        return self.file_service.read_csv(self.rel_path)

    def save_all(self, rows):
        self.file_service.write_csv(self.rel_path, self.headers, rows)

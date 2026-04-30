from datetime import datetime


class IDService:
    def __init__(self, config_service):
        self.config_service = config_service

    def generate_quote_id(self) -> str:
        cfg = self.config_service.data
        cfg["last_folio_number"] += 1
        self.config_service.save()
        year = datetime.now().strftime("%Y")
        number = cfg["last_folio_number"]
        return f"{cfg['folio_prefix']}-{year}-{number:04d}"

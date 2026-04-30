from pathlib import Path

from services.config_service import ConfigService
from services.file_service import CSVFileService
from services.id_service import IDService
from utils.logger import setup_logger
from controllers.app_controller import AppController
from views.main_view import MainView


def bootstrap_data(file_service, paths):
    file_service.ensure_csv(paths["clients"], ["id", "name", "rfc", "email", "phone"], [
        {"id": "C001", "name": "ACME SA", "rfc": "ACM010101AAA", "email": "compras@acme.com", "phone": "555-1111"}
    ])
    file_service.ensure_csv(paths["products"], ["id", "name", "description", "price", "cost"], [
        {"id": "P001", "name": "Laptop", "description": "Laptop 16GB RAM", "price": "15000", "cost": "11000"}
    ])
    file_service.ensure_csv(paths["quotes"], ["id", "client_id", "date", "subtotal", "tax", "total", "status"])
    file_service.ensure_csv(paths["quote_items"], ["quote_id", "product_id", "quantity", "unit_price", "total"])
    file_service.ensure_csv(paths["pricing_rules"], ["id", "type", "value", "condition"], [
        {"id": "R001", "type": "percentage", "value": "5", "condition": "quantity >= 10"}
    ])


def main():
    root = Path(__file__).parent
    config = ConfigService(root / "config.json")
    logger = setup_logger(root / config.data["file_paths"]["logs"])
    file_service = CSVFileService(root, logger)
    bootstrap_data(file_service, config.data["file_paths"])
    controller = AppController(config, file_service, IDService(config), logger)
    app = MainView(controller)
    app.mainloop()


if __name__ == "__main__":
    main()
